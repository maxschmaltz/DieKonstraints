import os
import re
from uuid import uuid4
import math
import pandas as pd
from tqdm.asyncio import tqdm
from collections import defaultdict
from typing import Optional, Tuple

from gecodb_compound_parser import Compound, perform_umlaut
from dereko_search import get_dereko_counts


def main():

    # In this script, we preprocess the annotated dataset from [schaefer_pankratz_2018]
    # original file: https://zenodo.org/records/1323211,
    # 'linkingelements/Data/Corpusstudy/Concordance.full.csv',
    # also saved under 'resources/schaefer_pankratz_2018/Concordance.full.csv' (private version).
    # This is the general preprocessing; further preprocessing for analysis of the external and 
    # internal plural effects (ExtPE, IntPE, respectively) are to be found in
    # 'data_utils/prepare_sp18_external.py' and 'data_utils/prepare_sp18_internal.py', respectively.
    #
    # Convention: (N=x) refers to the number of compound **tokens** in the dataset, 
    # while (UniqN=x) refers to the number of unique compound **lemmata** in the dataset.
    # 'Compounds' refers to 'compound tokens' unless specified otherwise.
    # 
    # The original dataset contains N=9415 compounds in Sg and Pl forms (different cases)
    # with individual or collective meaning of N1.
    # The columns are as follows:
    #   DocURL: URL of the source document.
    #   DocID: ID of the source document.
    #   SentID: ordinal number of the context sentence in the source document.
    #   LC: left context in the context sentence.
    #   Match: compound as it appears in the context sentence.
    #   RC: right context in the context sentence.
    #   N2Num: grammatical number of N2 (hence, the entire compound).
    #       Either "Sg" or "Pl", case not indicated.
    #   N2Typ: the meaning of N1 (as forced by N2).
    #       Either "ind" (individual), or "coll" (collective), or "konvc" (ambiguous).
    #   N1Lemma: the lemmatized N1.
    #   N1Pl: the plural type (marker) of N1.
    #   LE: whether the linking element is pluralic or not. Either 1 or 0, respectively.

    # Since our idea for investigating the ExtPE is to confront
    # contrastive pairs of compounds resulting from the same constituent combination
    # in Sg and Pl forms (e.g. 'Apfel' + 'Baum' is 'Apfelbaum' in Sg, will it become
    # 'Äpfelbäume' in Pl?), we need to know N2 of each compound unambiguously, too.
    # Thus, the main goal of this script is to parse the compounds as their appear
    # in the contexts (hence, compound wordforms) into combinations of N1+N2,
    # where both N1 and N2 appear in their lemmatized form. Besides, this parsing
    # will allow to identify duplicates if needed.
    #
    # Other than the described parsing, the script retrieves WCs of the dataset entries
    # from DeReKo, and does some further minor manipulations.

    # The overall preprocessing includes the following:
    #   1. Load the original dataset (henceforth referred to as Schäfer-Pankratz-Concordance).
    #   2. Load the relevant shards of CELEX2. We will not use CELEX-nouns
    #   originating from [shmalts_2026] for the following reasons:
    #       * CELEX-nouns set a minimal WC (DeReKo) threshold on the lemmata;
    #       however, we expect that less frequent compounds will be undergoing
    #       the ExtPE (as opposed to the IntPE, which works at the lexical level), 
    #       so we don't want to set any WC conditions. Furthermore, to validate 
    #       the hypothesis about low frequency of compounds affected by the ExtPE,
    #       we need to preserve compounds of all WCs.
    #       * CELEX-nouns only features NomSg, GenSg, and NomPl forms of its entries.
    #       Compounds in Schäfer-Pankratz-Concordance may occur in further wordforms.
    #   Specifically, we will need two files:
    #       * `gml.cd`: 'German Morphology, Lemmas'.
    #       * `gmw.cd`: 'German Morphology, Wordforms'.
    #   3. Apply initial cleaning. Specifically, compounds with _-e_ are removed,
    #   records with NaNs are removed, and unconventional spelling of a few N1 is corrected.
    #   4. Separate context sentence metadata and put it into a dedicated file.
    #   5. Parse the compounds into N1+N2 combinations (where both N1 and N2 appear 
    #   in their lemmatized form) with the help of CELEX2, reconstruct the 
    #   compound lemmata from there,  lemmatize N2 and reconstruct the lemmatized
    #   compounds in GeCoDB style.
    #   6. Retrieve word counts of compound lemmata/wordforms from DeReKo.
    #   7. Apply retrieved WCs to the dataset.
    #   8. Format the data.
    #   9. Separate the data into all, lemmatized, and non-lemnmatized compounds.
    #   Save the datasets.

    # As a result of the preprocessing, we obtain the following datasets:
    #
    #   * SP18-Meta 'resources/developed/sp18/sp18_meta.tsv' (N=9028):
    #   context sentence metadata of all compounds excluding the ones removed at step 3;
    #       context_id: the unique id of the context sentence. The context sentence results
    #           from joining the left context (LC), the compound (Match), 
    #           and the right context (RC) from the original data. This is the column
    #           by which this metadata can be joined back to the main dataset.
    #       doc_id: ID of the source document (original DocID).
    #       url: URL of the source document (original DocURL).
    #       sent_n: ordinal number of the context sentence in the source document 
    #           (original SentID).
    #
    #
    #   * SP18-All 'resources/developed/sp18/sp18_all.tsv' (N=9028, UniqN=7666):
    #   joint version of SP18 with both lemmatized and non-lemmatized compounds;
    #       gecodb: the GeCoDB notation of compound lemma/wordform.
    #       n1: N1 in the lemmatized form (original N1Lemma).
    #       n2: N2 in the lemmatized form, otherwise None. A non-empty value indicates
    #           that the compound is lemmatized.
    #       n1_pl_marker: the plural type (marker) of N1 (original N1Pl) converted to
    #           the GeCoDB notation.
    #       n1_sem: the meaning of N1 (as forced by N2) (original N2Typ).
    #           Either "ind" (individual), or "coll" (collective), or "konvc" (ambiguous).
    #       n2_num: grammatical number of N2 (hence, the entire compound) (original N2Num).
    #           Either "Sg" or "Pl", case not indicated.
    #       is_linker_pl: whether the linking element is pluralic or not (original LE).
    #           Either 1 or 0, respectively.
    #       wc: WC of lemma/wordform in DeReKo.
    #       context: context sentence. The context sentence results
    #           from joining the left context (LC), the compound (Match), 
    #           and the right context (RC) from the original data.
    #       context_id: the unique id of the context sentence. This is the column
    #           by which this metadata can be joined back to the main dataset.
    #
    #   * SP18 'resources/developed/sp18/sp18.tsv' (N=8212, UniqN=6889):
    #   default version of SP18 with lemmatized compounds only. Uses the same notation as SP18-All.
    #
    #   * SP18-NLemmatized 'resources/developed/sp18/leftovers/sp18_nlemmatized.tsv'
    #   (N=816, UniqN=781): default version of SP18 with lemmatized compounds only. 
    #   Uses the same notation as SP18-All except for missing N2 (never present).
    #
    #
    #
    #   * 'resources/developed/dereko_de_geq70_counts_lemmatized.tsv': updated cache file
    #       with DeReKo counts.
    #   
    #   * 'resources/developed/dereko_de_geq70_counts_nlemmatized.tsv': new cache file
    #       with DeReKo counts amd lemmata.

    # Thus, the data tree looks as follows:
    #
    #   Schäfer-Pankratz-Concordance
    #   the original data (N=9415)
    #   'resources/schaefer_pankratz_2018/Concordance.full.csv'
    #           |                                              \___
    #           |                                                  \______
    #           |                                                         \
    #         SP18-All -----------------> SP18-Meta                       removed records: compounds
    #   lemmatized and non-lemmatized       meta of SP18-all (N=9028)       with N1s 'Auge' (N=185),
    #   compounds (N=9028, UniqN=7666)         'resources/developed/         'Birne' (N=200), and 
    # 'resources/developed/sp18/sp18_all.tsv'      sp18/sp18_meta.tsv'        records with NaN (N=2)
    #           |                      \__
    #           |                         \_____
    #           |                               \
    #          SP18                      SP18-NLemmatized
    #   lemmatized compounds               non-lemmatized compounds
    #   (N=8212, UniqN=6889)                    (N=816, UniqN=781)
    # 'resources/developed/sp18/sp18.tsv'         'resources/developed/sp18/
    #                                               leftovers/sp18_nlemmatized.tsv'


    sp18_path = "resources/schaefer_pankratz_2018/Concordance.full.csv"
    celex_gml_path = "resources/Celex/german/gml/gml.cd"
    celex_gmw_path = "resources/Celex/german/gmw/gmw.cd"

    outdir = "resources/developed/sp18"

    outcsv_args = {
        "sep": "\t",
        "index": True,
        "header": True
    }

    # 1. Load the original dataset.

    # (N=9415)
    sp18 = pd.read_csv(
        sp18_path,
        sep="\t",
        header=0,
        index_col="Match",
        dtype=defaultdict(lambda: str, LE="int"),   # all str, LE int
        quoting=3   # = csv.QUOTE_NONE, separate by tabs only
    )


    # 2. Load the relevant shards of CELEX2.

    gml = pd.read_csv(
        celex_gml_path,
        sep="\\",
        header=None,
        dtype=str,
        usecols=[0, 1],
        names=["id", "lemma"],
        index_col="id"
    ).dropna()
    # only keep nouns
    gml = gml[gml["lemma"].str[0].str.isupper()]

    gmw = pd.read_csv(
        celex_gmw_path,
        sep="\\",
        header=None,
        dtype=str,
        usecols=[1, 3, 4],
        names=["wordform", "id", "forms"],
        index_col="id"
    ).dropna()

    # joining will automatically drop non-noun wordforms,
    # because they have no lemma in gml
    gmwl = gmw.join(gml["lemma"], how="inner")  \
        .reset_index(drop=True)  \
        .set_index("wordform")  \
        .sort_index()
    
    # CELEX2 spells umlauts as digraphs, convert those to umlauts 
    # to match Schäfer-Pankratz-Concordance
    def umlambda(x: str) -> str:
        # For each of the combinations of V + UU,
        # I searched DeReKo for the regex ".{1,5}VUU.{1,5}"
        # to see whether there are any frequent cases of VUU
        # that are not actually umlauted. For example, there are no
        # adequate examples of 'aae' that should not be umlauted
        # to 'aä', so we will assume that all cases of 'aae' 
        # are actually umlauted to 'aä'. On the other hand, there
        # are some cases of 'aue' that are not umlauted to 'aü',
        # such as 'Bauer' and related, so we will assume that 'aue' 
        # is not umlauted to 'aü' and will reflex that in the negative
        # lookbehind. The correct lookbehind assumptions may help correctly
        # parse cases like 'Diät' (from 'Diaet') that would otherwise
        # not be parsed with generic lookbehind assumptions.
        # Below I list examples
        # that support the present lookbehind assumptions.
        x = x.lower()
        # - aae: no adequate examples
        # - eae: no adequate examples
        # - iae: only proper names, e.g. 'Messiaen'
        # - oae: no adequate examples
        # - uae: only proper names, e.g. 'El Ouaer'
        # - yae: only proper names, e.g. 'Burlyaev'
        x = re.sub("ae", "ä", x, flags=re.IGNORECASE)
        # + aoe: 'Kakaoexport', 'Kakaoernte', ...
        # + eoe: 'Videoessay', 'Geoenetrgy', 'Stereoeffect', ...
        # + ioe: 'Bioethik', 'Radioeins', ...
        # - ooe: no adequate examples
        # - uoe: no adequate examples
        # - yoe: only proper names, e.g. 'Suyoen'
        x = re.sub("(?<![aei])oe", "ö", x, flags=re.IGNORECASE)
        # + aue: 'Bauer...', 'Frauen...', 'Mauer...', ...
        # + eue: 'Feuer...', 'Steuer...', ...
        # - iue: no adequate examples
        # - oue: 'Pirouette' (comps?); no adequate examples for 'oü' anyways
        # - uue: no adequate examples
        # - yue: only proper names, e.g. 'Ngyuen'
        x = re.sub("(?<![ae])ue", "ü", x, flags=re.IGNORECASE)
        return x

    gml["lemma"] = gml["lemma"].map(umlambda)

    gmwl.index = gmwl.index.map(umlambda)
    gmwl["lemma"] = gmwl["lemma"].map(umlambda)
    gmwl = gmwl[["lemma", "forms"]]


    # 3. Apply initial cleaning.

    # During the development, we discovered 154 mismatches between 
    # compound wordform reconstructions in `parse_sp18_comp()`
    # (so before lemmatization) and Schäfer-Pankratz-Concordance matches. The mismatching
    # compounds were built from six different N1.
    # Manual inspection of these mismatches revealed that
    # some compounds with N1s 'Dämon', 'Gerät', 'Geräusch', 'Schloss'
    # were spelled alternatively ('Daemon' etc.), and that compounds
    # with N1s 'Auge' and 'Birne' productively exhibit
    # alternation between _+n_ and _-e_ (!).
    # See compounds with these six N1s in 
    # 'resources/developed/sp18/leftovers/mismatches.csv'.
    # 
    # Here, we will correct the spellings of the first four N1s and remove
    # all compounds with the last two N1s.
    #
    # We report that after these two changes, all reconstructed compound
    # wordforms in `parse_sp18_comp()` (so before lemmatization) do match 
    # the original "Match" column of Schäfer-Pankratz-Concordance.

    # correct spellings
    for old, new in [
        ("Daemon", "Dämon"),
        ("Geraet", "Gerät"),
        ("Geraeusch", "Geräusch"),
        ("Schloß", "Schloss")
    ]:
        sp18.index = sp18.index.map(
            lambda x: x.replace(old, new)
            if x.startswith(old) else x
        )

    # remove compounds with N1s 'Auge' (N=185) and 'Birne' (N=200)
    sp18 = sp18[~sp18["N1Lemma"].isin(["Auge", "Birne"])]

    # drop NaN (N=2)
    sp18 = sp18.dropna()


    # 4. Separate context sentence metadata and put it into
    # a dedicated file.

    # Most probably, we won't need the context sentence metadata
    # such as source document URL and so on (also many URLs are now down).
    # To increase readability and reduce memory costs,
    # we decompose the dataframe and separate this metadata from it.
    # If needed, joining the metadata back to the main dataframe is trivial.

    # join the left and right contexts into a single column,
    # drop the original columns, and assign a unique id to each context
    sp18["context"] = sp18.LC + " " + sp18.index + " " + sp18.RC
    sp18.drop(columns=["LC", "RC"], inplace=True)
    sp18["context_id"] = [str(uuid4()) for _ in range(len(sp18))]
    sp18.head()

    # extract the document metadata
    # into a separate dataframe
    sp18_meta = sp18[
            ["context_id", "DocID", "DocURL", "SentID"]
        ]   \
        .rename(
            columns={"DocID": "doc_id", "DocURL": "url", "SentID": "sent_n"}
        )   \
        .reset_index(drop=True) \
        .set_index("context_id")    \
        .sort_index()

    # save metadata (N=9028)
    sp18_meta.to_csv(
        os.path.join(outdir, "sp18_meta.tsv"),
        **outcsv_args
    )

    # drop the metadata columns from the main dataframe
    sp18.drop(columns=["DocID", "DocURL", "SentID"], inplace=True)


    # 5. Parse the compounds into N1+N2 combinations (where both N1 and N2 appear 
    #   in their lemmatized form) with the help of CELEX2, reconstruct the 
    #   compound lemmata from there,  lemmatize N2 and reconstruct the lemmatized
    #   compounds in GeCoDB style.

    def lemmatize_n2(n2: str, expected_num: str) -> str:
        # no wordform found
        if n2 not in gmwl.index:
            return
        n2s = gmwl.loc[n2]
        # one wordform found, return its lemma
        if isinstance(n2s, pd.Series):
            return n2s["lemma"]
        else:
            # several wordforms found, 
            # check whether they all have the same lemma
            if n2s.lemma.nunique() == 1:
                # one lemma, ok
                return n2s.lemma.iloc[0]
            else:
                # try finding a variant that would correspond
                # to the annotated number of N2 (e.g. 'Spalte'
                # corresponds to 'Spalt' in Pl and 'Spalte' in Sg,
                # so searching for Sg wordform 'Spalte' will unambiguously
                # point to 'Spalte', while searching for Pl wordform 'Spalte'
                # will unambiguously point to 'Spalt');
                # otherwise: multiple variants matching the expected number,
                # unreliable parsing
                ncode = "P" if expected_num == "pl" else "S"
                matching_n2s = n2s[n2s["forms"].str.contains(ncode)]
                if matching_n2s.lemma.nunique() == 1:
                    # one lemma, ok
                    return matching_n2s.lemma.iloc[0]
            
    def parse_sp18_comp(
        comp: str,
        n1: str,
        pl_marker: str,
        has_linker: bool,
        n2_num: str,
        pbar: tqdm
    ) -> Tuple[str, str, str, str]:

        # contrary to [shmalts_2026], we will be differentiating between
        # _+er_ and _+=er_ in this study to be able to contrast
        # umlauting vs. non-umlauting pluralic linkers
        pl_gc_template = "_+={pl_marker}_" if "U" in pl_marker else "_+{pl_marker}_"
        # candidate N2 results from removing the (umlauted if needed) N1 prefix
        # from the compound; for example, the function removes 'Apfel'
        # from 'Apfelbaum' (`has_linker=False`) and 
        # 'Äpfel' from 'Äpfelkiste' (`has_linker=True`)
        maybe_uml = perform_umlaut if ("U" in pl_marker and has_linker) else lambda x: x
        pl_marker = pl_marker.replace("U", "")
        # to be updated later if needed
        linker = pl_marker if has_linker else ""
        n1_cstem = maybe_uml(n1) + linker
        n2 = re.sub(f"^{n1_cstem}", "", comp)

        # now, take the candidate n2 and try to lemmatize it
        # with the help of CELEX2, starting with a zero linker;
        # additionally, try eszett for cases like 'Fraß' ('Frass' in CELEX2)
        sz_in_n2s = [True, False] if "ß" in n2 else [False]
        for sz_in_n2 in sz_in_n2s:
            pot_linker = ""
            variant = n2.replace("ß", "ss") if sz_in_n2 else n2
            n2_lemma = lemmatize_n2(variant, expected_num=n2_num)
            if not n2_lemma and (match := re.search(r"^(s|es|ns|ens)", variant)):
                # try other possible non-pluralic linker
                pot_linker = match.group(0)
                n2_lemma = lemmatize_n2(variant[len(pot_linker):], expected_num=n2_num)
            # if the lemmatization was successful, update the linker
            # and revert the eszett if needed
            if n2_lemma:
                linker = pot_linker
                n2_lemma = n2_lemma.replace("ss", "ß") if sz_in_n2 else n2_lemma
                break
                
        # gecodb style
        pl_gc = pl_gc_template.format(pl_marker=pl_marker)
        # for cases like 'Apfelsscheiben' that has a non-pluralic linker
        # but still explicit linker -s-; no umlaut is possible in such case
        l_gc = pl_gc if has_linker else "_" if not linker else f"_+{linker}_"
        gecodb = f"{n1}{l_gc}{n2 if not n2_lemma else n2_lemma}"

        # recover compound lemma if possible
        lemma = Compound(gecodb).lemma if n2_lemma else None

        pbar.update(1)

        # gecodb: lemmatized compound if possible, otherwise
        # the original compound with the unlemmatized n2
        #
        # lemma: lemmatized compound if possible, otherwise None
        #
        # pl_gc: plural marker in gecodb style (e.g. _+=er_ instead of Uer)
        #
        # n2(_lemma): lemmatized n2 if possible, otherwise unlemmatized n2
        return gecodb, lemma, pl_gc, n2_lemma
    
    # this will return lemmatized N2 and lemmatized compounds
    # whenever possible; missing N2 and lemma indicate that the
    # corresponding N2 was not found in CELEX2, and the compound
    # could not be parsed reliably
    sp18.index = sp18.index.map(str.lower)
    for col in ["N1Lemma", "N2Num", "N2Typ"]:
        sp18[col] = sp18[col].map(str.lower)
    with tqdm(total=len(sp18), desc="Lemmatizing compounds") as pbar:
        sp18["gecodb"], sp18["lemma"], sp18["n1_pl_marker"], sp18["n2"] = zip(
            *sp18.apply(
                lambda row: parse_sp18_comp(
                    comp=row.name,
                    n1=row["N1Lemma"],
                    pl_marker=row["N1Pl"],
                    has_linker=int(row["LE"]),
                    n2_num=row["N2Num"],
                    pbar=pbar
                ),
                axis=1
            )
        )


    # 6. Retrieve word counts of compound lemmata/wordforms from DeReKo.

    # The WCs are retrieved under the same procedure as described in [shmalts_2026].
    # DeReKo accessed in the middle of June 2026.
    #
    # We have two scenarios:
    #   * Lemmatized compounds may be searched directly.
    #   * Non-lemmatized compounds will be first searched as a simple text search.
    #   If there are matches, the lemma annotation will be retrieved
    #   from the first match, and a consequent search for the retrieved lemma
    #   will be performed.
    # 
    # Thus, the search will accomplish two goals:
    #   * Retrieve lemma annotation for non-lemmatized compounds whenever possible.
    #   * Retrieve counts: total word count of all wordforms for lemmatized compounds
    #   and non-lemmatized compounds that we able to be lemmatized, and 
    #   total count of compound wordforms otherwise.

    def dereko_wrapper(
        input_lemmata: list[str],
        batch_size: Optional[int]=1000,
        **kwargs
    ) -> Tuple[list[int], list[str]]:

        # run in batches to enforce regular caching
        freqs = []
        output_lemmata = []

        progress_bar = tqdm(
            total=math.ceil(len(input_lemmata) / batch_size),
            desc="Retrieving KorAP frequencies in batches"
        )

        for batch_start in range(0, len(input_lemmata), batch_size):
            batch = input_lemmata[batch_start:batch_start + batch_size]
            batch_freqs, batch_lemmata = get_dereko_counts(batch, **kwargs)
            freqs.extend(batch_freqs)
            output_lemmata.extend(batch_lemmata)
            progress_bar.update(1)
            
        return freqs, output_lemmata

    # get counts for lemmatized compounds (N=8073, UniqN=6813)
    input_lemmata_l = sp18[pd.notna(sp18["lemma"])].lemma \
        .map(str.capitalize).unique().tolist()
    freqs_l, _ = dereko_wrapper(
        input_lemmata_l,
        resolve_sz=True,
        is_base=True
    )

    # get counts for non-lemmatized compounds (N=955, UniqN=954)
    input_lemmata_nl = sp18[pd.isna(sp18["lemma"])].index \
        .map(str.capitalize).unique().tolist()
    freqs_nl, output_lemmata = dereko_wrapper(
        input_lemmata_nl,
        resolve_sz=True,
        is_base=False
    )


    # 7. Apply retrieved WCs to the dataset.

    # We have three scenarios of WC application.
    #   * Scenario 1: lemmatized compounds. Only add the WCs to the records.
    #   * Scenario 2: non-lemmatized compounds that couldn't be lemmatized.
    #   Only add the WCs to the records. The N2s, hence, the compounds 
    #   remain unlemmatized.
    #   * Scenario 3: non-lemmatized compounds that could be lemmatized.
    #   Even though the compound lemma was found, it doesn't that the N2
    #   would. Remember that it is correct N2, not lemma, that is crucial
    #   in this preprocessing. Therefore, we will try to parse these compounds
    #   again in a fashion similar to the first parsing, but now with the
    #   lemmata at our disposal. For example, 'Zahnpasten' could not be
    #   parsed in the first iteration because Pl form 'Pasten' is ambiguous
    #   for 'Paste' and 'Pasta'; however, knowing its lemma 'Zahnpaste' 
    #   from DeReKo allows to unambiguously parse the Sg form 'Zahnpaste'
    #   into 'Zahn' + 'Paste'. On the other hand, even knowing the lemma
    #   'Muttersprachler' does not allow us to reliably parse the compound into
    #   'Mutter' + 'Sprachler' since 'Sprachler' is not present in CELEX2;
    #   it could have theoretically be 'Mutter-s-Prachler'.
    #   Thus, in scenario three, we try to reparse the compounds with its lemmata,
    #   and then have two sub-scenarios:
    #       * Scenario 3.1: newly lemmatized compounds that could be reparsed.
    #       Add the WCs to the records, update the N2s, the compound
    #       lemmata (both were None up to this point), 
    #       and the GeCoDB notations in the records.
    #       * Scenario 3.2: newly lemmatized compounds that couldn't be reparsed.
    #       Only add the WCs to the records (NB: these are wordform counts
    #       and not lemma counts as in other cases).

    def verify_n2(n2: str) -> bool:
        # check whether this lemma even exists
        n2s = gml[gml["lemma"] == n2]
        return not n2s.empty

    # TODO: join with `parse_sp18_comp()`?
    def verify_sp18_comp(
        comp: str,
        n1: str,
        pl_marker: str,
        has_linker: bool,
        pbar: tqdm
    ) -> Tuple[str, str]:
        
        pl_gc_template = "_+={pl_marker}_" if "U" in pl_marker else "_+{pl_marker}_"
        maybe_uml = perform_umlaut if ("U" in pl_marker and has_linker) else lambda x: x
        pl_marker = pl_marker.replace("U", "")
        # to be updated later if needed
        linker = pl_marker if has_linker else ""
        n1_cstem = maybe_uml(n1) + linker
        n2 = re.sub(f"^{n1_cstem}", "", comp)

        # now, take the candidate n2 and try to verify it
        # with the help of CELEX2, starting with a zero linker;
        # additionally, try eszett for cases like 'Fraß' ('Frass' in CELEX2)
        sz_in_n2s = [True, False] if "ß" in n2 else [False]
        for sz_in_n2 in sz_in_n2s:
            pot_linker = ""
            variant = n2.replace("ß", "ss") if sz_in_n2 else n2
            n2_verified = verify_n2(variant)
            if not n2_verified and (match := re.search(r"^(s|es|ns|ens)", n2)):
                # try other possible non-pluralic linker
                pot_linker = match.group(0)
                n2_verified = verify_n2(variant[len(pot_linker):])
                if n2_verified:
                    # if the lemmatization was successful, update the linker
                    n2 = n2[len(pot_linker):]
                    n2 = n2.replace("ss", "ß") if sz_in_n2 else n2
                    linker = pot_linker

        # gecodb style
        pl_gc = pl_gc_template.format(pl_marker=pl_marker)
        # for cases like 'Apfelsscheiben' that has a non-pluralic linker
        # but still explicit linker -s-; no umlaut is possible in such case
        l_gc = pl_gc if has_linker else "_" if not linker else f"_+{linker}_"
        gecodb = f"{n1}{l_gc}{n2}"

        # discard N2 if it was not verified
        n2 = None if not n2_verified else n2

        pbar.update(1)

        return gecodb, n2

    def apply_dereko_counts(row: pd.Series, pbar: tqdm) -> Tuple[str, str, float]:

        gecodb, n2_lemma = row["gecodb"], row["n2"]

        # scenario 1: lemmatized compounds
        if pd.notna(n2_lemma):
            count = freqs_l[input_lemmata_l.index(row["lemma"].capitalize())]
        # scenario 2: non-lemmatized compounds that couldn't be lemmatized
        # + scenario 3: non-lemmatized compounds that could be lemmatized.
        else:
            # get either retrieved lemma and its count,
            # or no lemma and the count for the original wordform
            ind = input_lemmata_nl.index(row.name.capitalize())
            lemma = output_lemmata[ind]
            count = freqs_nl[ind]
    
        # scenario 3 (continuation): non-lemmatized compounds that could be lemmatized.
        if pd.isna(n2_lemma) and pd.notna(lemma):
            lemma = lemma.lower()
            # scenario 3.1: newly lemmatized compounds that could be reparsed
            #   will result in GeCoDB of compound lemma and a lemmatized N2;
            # scenario 3.2: newly lemmatized compounds that couldn't be reparsed
            #   will result in GeCoDB of compound wordform and a None
            gecodb, n2_lemma = verify_sp18_comp(
                comp=lemma, # !
                n1=row["N1Lemma"],
                pl_marker=row["N1Pl"],
                has_linker=int(row["LE"]),
                pbar=pbar
            )

        # restore eszett; remember, a count ending
        # in 0.3 means that a compound that contained an eszett
        # written as 'ss', did not get any hits in DeReKo with its
        # orthography but did so after restoring the eszett to 'ß';
        # an example from the dataset:
        # 'Bildergrösse' (WC=0) vs 'Bildergröße' (WC=23)
        if round(count % 1, 1) == 0.3:
            gecodb = gecodb.replace("ss", "ß")
            if isinstance(n2_lemma, str):
                n2_lemma = n2_lemma.replace("ss", "ß")
            # the current index ("Match") will be dropped soon,
            # so no need to update it
            count = round(count - 0.3)

        return gecodb, n2_lemma, count

    # apply DeReKo counts; whenever applicable, also insert the retrieved lemma
    # and update the gecodb and the N2 column for non-lemmatized compounds
    # (total retrieved compound lemmata N=359, verified N=139)
    retrieved_lemmata = [o for o in output_lemmata if not pd.isna(o)]
    with tqdm(desc="Applying DeReKo counts", total=len(retrieved_lemmata)) as pbar:
        sp18["gecodb"], sp18["n2"], sp18["wc"] = zip(
            *sp18.apply(
                lambda row: apply_dereko_counts(row, pbar=pbar),
                axis=1
            )
        )


    # 8. Format the data.

    # discard lemma: it was only used for a more convenient extraction
    # of input for DeReKo; now its role will be replaced by the N2 column
    # which will contain the lemmatized N2 whenever applicable,
    # otherwise indicating that the compound is not lemmatized
    sp18 = sp18[
            [
                "gecodb", "N1Lemma", "n2", "n1_pl_marker",
                "N2Typ", "N2Num", "LE", "wc",
                "context", "context_id"
            ]
        ]   \
        .rename(
            columns={
                "N1Lemma": "n1", "N2Typ": "n1_sem",
                "N2Num": "n2_num", "LE": "is_linker_pl"
            }
        )   \
        .reset_index(drop=True) \
        .set_index("gecodb")    \
        .sort_index()   \

    sp18["wc"] = sp18["wc"].astype(int)


    # 9. Separate the data into all, lemmatized, and non-lemnmatized compounds.
    # Save the datasets.

    # From here on, we will have three versions of the dataset
    # because reliable deduplication and detection of contrastive Sg-Pl pairs
    # depends on the lemmatization of N2 (hence, the entire compound):
    # * A joint version with both lemmatized and not lemmatized compounds.
    # Will be used for the analysis of the IntPE only.
    # Caution should be exercised when interpreting the results
    # of the IntPE analysis based on the joint version.
    # * A version with lemmatized compounds only. We will extract the
    # contrastive pairs from this version and use it for the analysis of the ExtPE.
    # * A version with not-lemmatized compounds only. Saved only in favor
    # processing consistency.
    
    # joint version (N=9028, UniqN=7666)
    sp18_all = sp18.copy()
    sp18_all.to_csv(
        os.path.join(outdir, "sp18_all.tsv"),
        **outcsv_args
    )

    # default version: lemmatized compounds only 
    # (originally N=8073, after DeReKo search and N2 verification became
    # N=8212, UniqN=6889)
    sp18 = sp18_all[sp18_all["n2"].notna()]
    sp18.to_csv(
        os.path.join(outdir, "sp18.tsv"),
        **outcsv_args
    )

    # not-lemmatized compounds 
    # (originally N=955, after DeReKo search and N2 verification became
    # N=816, UniqN=781)
    sp18_nlemmatized = sp18_all[sp18_all["n2"].isna()]
    sp18_nlemmatized.drop(columns=["n2"], inplace=True)
    sp18_nlemmatized.to_csv(
        os.path.join(outdir, "leftovers/sp18_nlemmatized.tsv"),
        **outcsv_args
    )


if __name__ == "__main__":
    main()