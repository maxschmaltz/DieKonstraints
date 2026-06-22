# %%
import os
import pandas as pd
from uuid import uuid4
from tqdm.asyncio import tqdm
import re
from collections import defaultdict
import math
from typing import Optional, Tuple

# %%
from gecodb_compound_parser import Compound, perform_umlaut
from dereko_search import get_dereko_counts

# %%
sp18_path = "resources/schaefer_pankratz_2018/Concordance.full.csv"
celex_gml_path = "resources/Celex/german/gml/gml.cd"
celex_gmw_path = "resources/Celex/german/gmw/gmw.cd"

outdir = "resources/developed/sp18"

outcsv_args = {
    "sep": "\t",
    "index": True,
    "header": True
}

# %%
sp18 = pd.read_csv(
    sp18_path,
    sep="\t",
    header=0,
    index_col="Match",
    dtype=defaultdict(lambda: str, LE="int"),   # all str, LE int
    quoting=3   # = csv.QUOTE_NONE, separate by tabs only
)
sp18.head()

# %%
def umlambda(x: str) -> str:
    x = x.lower()
    x = re.sub("(?<![aeiouy])ae", "ä", x, flags=re.IGNORECASE)
    x = re.sub("(?<![aeiouy])oe", "ö", x, flags=re.IGNORECASE)
    x = re.sub("(?<![aeiouy])ue", "ü", x, flags=re.IGNORECASE)
    return x

# %%
gml = pd.read_csv(
    celex_gml_path,
    sep="\\",
    header=None,
    dtype=str,
    usecols=[0, 1],
    names=["id", "lemma"],
    index_col="id"
).dropna()

# keep only nouns
gml = gml[gml["lemma"].str[0].str.isupper()]

gml

# %%
gmw = pd.read_csv(
    celex_gmw_path,
    sep="\\",
    header=None,
    dtype=str,
    usecols=[1, 3, 4],
    names=["wordform", "id", "forms"],
    index_col="id"
).dropna()

gmw

# %%
# joining will automatically drop non-noun wordforms,
# because they have no lemma in gml
gmwl = gmw.join(gml["lemma"], how="inner")  \
    .reset_index(drop=True)  \
    .set_index("wordform")  \
    .sort_index()

gml["lemma"] = gml["lemma"].map(umlambda)

gmwl.index = gmwl.index.map(umlambda)
gmwl["lemma"] = gmwl["lemma"].map(umlambda)
gmwl = gmwl[["lemma", "forms"]]

gmwl

# %%
# Comparing the original Match column values with
# with reconstructions from `parse_sp18_comp()`
# (before lemmatization to NomSg with the help of CELEX2!)
# during development of this module
# revealed 154 mismatches in compounds built from
# six different N1. Manual inspection of these mismatches revealed that
# some compounds with N1s 'Dämon', 'Gerät', 'Geräusch', 'Schloss'
# were spelled alternatively, and that compounds
# with N1s 'Auge' and 'Birne' productively exhibit
# alternation between _+n_ and _-e_ (!).
# See more in 'resources/developed/sp18/leftovers/mismatches.csv'.
# Thus, we will correct
# the spellings of the first four N1s and remove
# all compounds with the last two N1s.

# After these two changes, all reconstructed compounds
# after `parse_sp18_comp()` do match the original Match column
# (before lemmatization to NomSg with the help of CELEX2!).

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

# %%
# drop NaN (2 rows only)
sp18 = sp18.dropna()

# %%
# extract document metadata from the dataset;
# most probably, we won't need it (also
# many URLs are now down, anyways),
# so by decomposing the dataframe, we can
# reduce processing effort; on the other hand,
# joining the metadata back to the main dataframe
# is easy, so we can always do it later if needed

# first, join the left and right contexts into a single column,
# drop the original columns, and assign a unique id to each context
sp18["context"] = sp18.LC + " " + sp18.index + " " + sp18.RC
sp18.drop(columns=["LC", "RC"], inplace=True)
sp18["context_id"] = [str(uuid4()) for _ in range(len(sp18))]
sp18.head()

# %%
# now, extract the document metadata
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

sp18_meta.to_csv(
    os.path.join(outdir, "sp18_meta.tsv"),
    **outcsv_args
)
sp18_meta.head()

# %%
# finally, drop the metadata columns
# from the main dataframe
sp18.drop(columns=["DocID", "DocURL", "SentID"], inplace=True)
sp18.head()

# %%
# First, we need to be able to reconstruct the whole
# compound composition. We need that for three reasons:
# 1. To be able to revert the compounds to NomSg,
# which, in its turn, is required to identify duplicates;
# 2. Beside duplicates removal, we will also be able to
# identify contrastive pairs from the same constituents
# but with pluralic vs. non-pluralic linkers. This would
# be needed to assess the external plural effect
# following the method suggested in [pankratz_2017:20]
# (even though the examples are given for the internal plural effect).
# There is a change that the findings with this approach
# will be different as in [schaefer_pankratz_2018:26] since they
# do not contrast such pairs but rather compare all compounds in Pl forms
# to those in Sg forms.
# 3. Finally, similarly to [shmalts_2026], we would want
# to filter out the constituents not present in CELEX-nouns.

def lemmatize_n2(n2: str, expected_num: str) -> str:
    if n2 not in gmwl.index:
        return
    n2s = gmwl.loc[n2]
    if isinstance(n2s, pd.Series):  # one row found
        return n2s["lemma"]
    else:
        if n2s.lemma.nunique() == 1:
            # one variant, ok
            return n2s.lemma.iloc[0]
        else:
            # try finding a variant
            # that would correspond
            # to the annotated number of N2;
            # otherwise: multiple variants matching the expected number,
            # unreliable parsing
            ncode = "P" if expected_num == "pl" else "S"
            matching_n2s = n2s[n2s["forms"].str.contains(ncode)]
            if matching_n2s.lemma.nunique() == 1:
                # one variant, ok
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
    maybe_uml = perform_umlaut if ("U" in pl_marker and has_linker) else lambda x: x
    pl_marker = pl_marker.replace("U", "")
    # to be updated later if needed
    linker = pl_marker if has_linker else ""
    n1_cstem = maybe_uml(n1) + linker
    n2 = re.sub(f"^{n1_cstem}", "", comp)

    # now, take the resulting n2 and try to lemmatize it to NomSg 
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
        # and revers the eszett if needed
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

    # recover lemma if possible
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


def verify_n2(n2: str) -> bool:
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
    
    # contrary to [shmalts_2026], we will be differentiating between
    # _+er_ and _+=er_ in this study to be able to contrast
    # umlauting vs. non-umlauting pluralic linkers
    pl_gc_template = "_+={pl_marker}_" if "U" in pl_marker else "_+{pl_marker}_"
    maybe_uml = perform_umlaut if ("U" in pl_marker and has_linker) else lambda x: x
    pl_marker = pl_marker.replace("U", "")
    # to be updated later if needed
    linker = pl_marker if has_linker else ""
    n1_cstem = maybe_uml(n1) + linker
    n2 = re.sub(f"^{n1_cstem}", "", comp)

    # now, take the resulting n2 and try to lemmatize it to NomSg 
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



# %%
sp18.index = sp18.index.map(str.lower)
for col in ["N1Lemma", "N2Num", "N2Typ"]:
    sp18[col] = sp18[col].map(str.lower)
sp18.head()

# %%
with tqdm(total=len(sp18), desc="Lemmatizing compounds") as pbar:
    sp18["gecodb"], sp18["lemma"], sp18["n1_pl_marker"], sp18["n2"] = zip(
        *sp18.apply(
            # try top lemmatize using CELEX2
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

sp18.head()

# %%
# Retrieve word counts from DeReKo; we have two scenarios:
# Lemmatized compounds may be searched directly;
# Non-lemmatized compounds will be first searched as a simple text search;
# if there are matches, the lemma annotation will be retrieved
# from the first match, and a consequent search for the retrieved lemma
# will be performed. This, the search will accomplish two goals:
# 1. It will allow us to retrieve counts for both lemmatized compounds
# (total word count of all wordforms) and counts for non-lemmatized compounds
# (only total count of the corresponding wordform).
# 2. It will partly retrieve the lemma annotation for non-lemmatized compounds.
def dereko_wrapper(
    input_lemmata: list[str],
    batch_size: Optional[int]=1000,
    **kwargs
) -> Tuple[list[int], list[str]]:

    # get dereko WCs; run in batches to enforce regular caching;
    # the cache is stored in 
    # resources/comp_constr_corp_study_mar26/dereko_de_geq70_counts.tsv
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

# %%
# get counts for lemmatized compounds (N=8009, UniqN=6755)
input_lemmata_l = sp18[~pd.isna(sp18["lemma"])].lemma \
    .map(str.capitalize).unique().tolist()

freqs_l, _ = dereko_wrapper(
    input_lemmata_l,
    resolve_sz=True,
    is_base=True
)

# %%
# get counts for non-lemmatized compounds (N=1019, UniqN=1018)
input_lemmata_nl = sp18[pd.isna(sp18["lemma"])].index \
    .map(str.capitalize).unique().tolist()

# non-empty output_lemmata: (N=380)
freqs_nl, output_lemmata = dereko_wrapper(
    input_lemmata_nl,
    resolve_sz=True,
    is_base=False
)

# %%
def apply_dereko_counts(row: pd.Series, pbar: tqdm) -> Tuple[str, str, float]:

    gecodb, n2_lemma = row["gecodb"], row["n2"]

    if pd.notna(n2_lemma):

        # lemmatized compound, get the count for the lemma
        count = freqs_l[input_lemmata_l.index(row["lemma"].capitalize())]
        
    else:

        # non-lemmatized compound, get
        # either retrieved lemma and its count,
        # or no lemma and the count for the original wordform
        ind = input_lemmata_nl.index(row.name.capitalize())
        lemma = output_lemmata[ind]
        count = freqs_nl[ind]
 
    # Now we need to parse the compounds again, for which DeReKo found lemmata
    # (with correct eszett) for three reasons:
    # 1. To be able to identify/verify the correct N2 lemma to be able
    # to identify duplicates and contrastive pairs for the analysis 
    # of the internal and external plural effects; it may be the case
    # that the N2 won't be verified (even though the lemma is in place),
    # in which case the entry can't be used for the analysis of the 
    # external plural effect.
    # 2. To be able to identify the correct non-pluralic linker.
    # 3. To update N2 (if applicable) for newly lemmatized compounds:
    # otherwise these rows will contain the newly acquired lemmata
    # from DeReKo but unparsed N2s which were not found in CELEX2;
    # for example 'Apfelspalten' was not able to be parsed to 'Apfelspalte' with CELEX2,
    # so the gecodb column contains 'apfel_spalten' (instead of 'apfel_spalte'),
    # and the N2 column contains Spalten (instead of Spalte);
    # however, DeReKo search for 'Apfelspalten' did return lemma 'Apfelspalte',
    # from where the desired variants are deductible,
    # so we need to update the two columns for this row to reflect the new information.
    if pd.isna(n2_lemma) and pd.notna(lemma):
        lemma = lemma.lower()
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
        if pd.notna(n2_lemma):
            n2_lemma = n2_lemma.replace("ss", "ß")
        # the current index will be dropped soon,
        # so no need to update it
        count = round(count - 0.3)

    return gecodb, n2_lemma, count

# %%
# apply DeReKo counts; whenever applicable, also insert the retrieved lemma
# and update the gecodb and the N2 column for non-lemmatized compounds
retrieved_lemmata = [o for o in output_lemmata if not pd.isna(o)]
with tqdm(desc="Applying DeReKo counts", total=len(retrieved_lemmata)) as pbar:
    sp18["gecodb"], sp18["n2"], sp18["wc"] = zip(
        *sp18.apply(
            lambda row: apply_dereko_counts(row, pbar=pbar),
            axis=1
        )
    )

# %%
# discard lemma; now its role will be replaced by the N2 column
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


sp18.sample(5)

# %%
# From here on, we will have two versions of the dataset
# because reliable deduplication and detection of contrastive Sg-Pl pairs
# depends on the lemmatization of N2:
# 1. A version with lemmatized compounds only. We will extract the
# contrastive pairs from this version and use
# it for the analysis of the external plural effect.
# The compounds remaining after this extraction
# will be deduplicated and used for the analysis of
# the internal plural effect.
# 2. A joint version with both lemmatized and not lemmatized compounds.
# Will be used for the analysis of the internal plural effect only.
# Caution should be exercised when interpreting the results
# of the internal plural effect analysis based on the joint version.

# not-lemmatized compounds 
# (originally N=1266, after DeReKo search and manual correction N=825)
sp18_nlemmatized = sp18[sp18["n2"].isna()]
sp18_nlemmatized.drop(columns=["n2"], inplace=True)
sp18_nlemmatized.to_csv(
    os.path.join(outdir, "leftovers/sp18_nlemmatized.tsv"),
    **outcsv_args
)

# joint version (N=9028)
sp18_all = sp18.copy()
sp18_all.to_csv(
    os.path.join(outdir, "sp18_all.tsv"),
    **outcsv_args
)

# default version: lemmatized compounds only 
# (originally N=7762, after DeReKo search and manual correction N=8203)
sp18 = sp18_all[sp18_all["n2"].notna()]
sp18.to_csv(
    os.path.join(outdir, "sp18.tsv"),
    **outcsv_args
)


# %%
# extract contrastive Sg-Pl pairs from the lemmatized version
sp18["const_comb"] = sp18["n1"] + "+" + sp18["n2"]
ident_const_all = sp18[sp18.duplicated(subset="const_comb", keep=False)]    \
    .sort_values("const_comb")  \
    .reset_index(drop=False)    \
    .set_index("const_comb")

ident_const_all.to_csv(
    os.path.join(outdir, "external_effect/ident_const_all.tsv"),
    **outcsv_args
)
ident_const_all

# %%
# First, we need to leave out compounds that do 
# not exhibit an alternation of Sg vs. Pl forms,
# that is, always occurred in either Sg or Pl form, but not in both.

ic_nums_data = {
    const_comb: {
        "sg_form": len(
            group[group["n2_num"] == "sg"]
        ),
        "pl_form": len(
            group[group["n2_num"] == "pl"]
        )
    }
    for const_comb, group in ident_const_all.groupby("const_comb")
}

ic_nums = pd.DataFrame.from_dict(ic_nums_data, orient="index")
# ic_nums.to_csv(
#     os.path.join(outdir, "external_effect/ic_nums.tsv"),
#     **outcsv_args
# )
ic_nums

# %%
# only Sg forms (N=832)
ic_nalt_sg = ic_nums[ic_nums["pl_form"] == 0].index
ident_const_all.loc[ic_nalt_sg].to_csv(
    os.path.join(outdir, "external_effect/ic_nalt_sg.tsv"),
    **outcsv_args
)

# only Pl forms (N=219)
ic_nalt_pl = ic_nums[ic_nums["sg_form"] == 0].index
ident_const_all.loc[ic_nalt_pl].to_csv(
    os.path.join(outdir, "external_effect/ic_nalt_pl.tsv"),
    **outcsv_args
)

# alternating forms (N=2129)
ident_const_alt = ident_const_all[
    ~ident_const_all.index.isin(ic_nalt_sg) &
    ~ident_const_all.index.isin(ic_nalt_pl)
]
ident_const_alt.to_csv(
    os.path.join(outdir, "external_effect/ic_alt_all.tsv"),
    **outcsv_args
)
ident_const_alt

# %%
# We assume that since in standard (not colloquial)
# German, the combination of N1 and the linker should
# remain the same in Sg and Pl compound form,
# (e.g. Apfelbaum vs. Apfelbäume),
# and since the internal plural effect should enforce
# the pluralic linker, nouns that undergo the
# internal plural effect may not exhibit a reliable
# alternation in Sg vs. Pl forms, since they would
# receive the pluralic linker in its base form (Sg)
# and bring it to the Pl form. This is exemplified 
# by the examples in the dataset of Äpfelkiste vs. Äpfelkisten,
# or Liederabend vs. Liederabende.
# We therefore further separate the data onto the subsets
# of alternating compounds with no internal plural effect
# and those with the internal plural effect.

# internal plural effect (N=341)
ic_alt_ipe = ident_const_alt[
    ~(ident_const_alt["n1_sem"] == "ind")
]
ic_alt_ipe.to_csv(
    os.path.join(outdir, "external_effect/ic_alt_ipe.tsv"),
    **outcsv_args
)

# internal plural effect (N=1788)
ic_alt_nipe = ident_const_alt[
    ident_const_alt["n1_sem"] == "ind"
]
ic_alt_nipe.to_csv(
    os.path.join(outdir, "external_effect/ic_alt_nipe.tsv"),
    **outcsv_args
)
ic_alt_nipe

# %%
# Now furthermore, as we know, semantic constraints
# are not the only constraints that govern linker choice.
# There may be cases where a constituent
# with no internal plural effect may still consistently 
# receive a pluralic linker (with no plural cue) due to other constraints,
# e.g. phonological or morphological. Since a compound with a pluralic linker
# in Sg will most probably appear with the same linker in Pl
# (see the explanation above), we expect to see external effect (if it exists)
# only in the compounds that usually take a zero linker in Sg form.
# Otherwise, if the compound usually takes a pluralic linker in Sg form
# (be it due to the internal plural effect or other constraints),
# the chances are that it will also take a pluralic linker in Pl form, and thus
# the external plural effect will be masked. This is exemplified
# by the examples in the dataset of Katzenfell vs. Katzenfelle,
# Kinderbuch vs. Kinderbücher.
# Therefore, we will here separate the subset into the group
# of compounds that mostly take a zero linker in Sg form
# and the group of compounds that mostly take a pluralic linker in Sg form.

ic_alt_nipe_sg_links_data = {
    const_comb: {
        "sg_l": len(
            group[
                (group["n2_num"] == "sg") &
                (~group["is_linker_pl"])
            ]
        ),
        "pl_l": len(
            group[
                (group["n2_num"] == "sg") &
                (group["is_linker_pl"])
            ]
        )
    }
    for const_comb, group in ic_alt_nipe.groupby("const_comb")
}

ic_alt_nipe_sg_links = pd.DataFrame.from_dict(ic_alt_nipe_sg_links_data, orient="index")
# ic_nums.to_csv(
#     os.path.join(outdir, "external_effect/ic_nums.tsv"),
#     **outcsv_args
# )
ic_alt_nipe_sg_links

# %%
# mostly pluralic linker in the Sg form (N=569)
ic_alt_nipe_pl_l = ic_alt_nipe_sg_links[
    ic_alt_nipe_sg_links["pl_l"] >
    ic_alt_nipe_sg_links["sg_l"]
].index
ic_alt_nipe.loc[ic_alt_nipe_pl_l].to_csv(
    os.path.join(outdir, "external_effect/ic_alt_nipe_pl_l.tsv"),
    **outcsv_args
)

# mostly zero linker in the Sg form (N=1219)
ic_alt_nipe_sg_l = ic_alt_nipe[
    ~ic_alt_nipe.index.isin(ic_alt_nipe_pl_l)
]
ic_alt_nipe_sg_l.to_csv(
    os.path.join(outdir, "external_effect/ic_alt_nipe_sg_l.tsv"),
    **outcsv_args
)
ic_alt_nipe_sg_l

# %%
ic_alt_nipe_sg_l_sum_data = {}
for const_comb, group in ic_alt_nipe_sg_l.groupby("const_comb"):
    for num in ["sg", "pl"]:
        ic_alt_nipe_sg_l_sum_data[(const_comb, f"num_{num}")] = {
            "l_sg": len(
                group[(group["n2_num"] == num) & (~group["is_linker_pl"])]
            ),
            "l_pl": len(
                group[(group["n2_num"] == num) & (group["is_linker_pl"])]
            )
        }

ic_alt_nipe_sg_l_sum = pd.DataFrame(ic_alt_nipe_sg_l_sum_data).T
ic_alt_nipe_sg_l_sum["pl_share"] = ic_alt_nipe_sg_l_sum["l_pl"] / (
    ic_alt_nipe_sg_l_sum["l_sg"] + ic_alt_nipe_sg_l_sum["l_pl"]
)
# ic_alt_nipe_sg_l_sum.to_csv(
#     os.path.join(outdir, "external_effect/ic_alt_nipe_sg_l_sum.tsv"),
#     **outcsv_args
# )
ic_alt_nipe_sg_l_sum

# %%
ic_alt_nipe_sg_l_shares = ic_alt_nipe_sg_l_sum.unstack()["pl_share"]
ic_alt_nipe_sg_l_shares = ic_alt_nipe_sg_l_shares[["num_sg", "num_pl"]]
ic_alt_nipe_sg_l_shares

# %%
# A few constituent combinations (supposedly) exhibit
# variation between Sg and Pl-like meaning of N1
# in different entries depending on the context (refer to the dataset).
# These are:
# 'bad+ausstellung', 'bett+belegung', 'bucht+system', 'ei+paket',
# 'ei+sack', 'element+häufigkeit', 'element+zuordnung', 'gerät+verlust',
# 'gerät+wart', 'hand+kontakt', 'hund+buch', 'kommune+bewegung',
# 'kommune+tag', 'loch+dichte', 'nation+tafel', 'produkt+familie',
# 'schloss+tour', 'schwester+genossenschaft', 'stadt+tour', 'vogel+buch',
# 'vogel+zimmer', 'zahn+differenz'.
# Since this difference points to the internal rather than external plural effect,
# we exclude these combinations from the analysis of the external plural effect.
inconsistent_n1_sem = ic_alt_nipe_sg_l_shares[ic_alt_nipe_sg_l_shares.isna().any(axis=1)]
ic_alt_nipe_sg_l.loc[inconsistent_n1_sem.index].to_csv(
    os.path.join(outdir, "leftovers/inconsistent_n1_sem.tsv"),
    **outcsv_args
)

ic_alt_nipe_sg_l_shares.dropna(inplace=True)
ic_alt_nipe_sg_l = ic_alt_nipe_sg_l[
    ~ic_alt_nipe_sg_l.index.isin(inconsistent_n1_sem.index)
]

ic_alt_nipe_sg_l

# %%


# %%


# %%


# %%
from scipy.stats import chi2_contingency
from statsmodels.stats.contingency_tables import Table

# %%
res_outdir = "../out/external_effect"

outcsv_args = {
    "sep": "\t",
    "index": True,
    "header": True
}

# %%
ic_alt_nipe_sg_l_shares_desc = ic_alt_nipe_sg_l_shares.describe()
ic_alt_nipe_sg_l_shares_desc.to_csv(
    os.path.join(res_outdir, "ic_alt_nipe_sg_l/desc.tsv"),
    **outcsv_args
)
ic_alt_nipe_sg_l_shares_desc

# %%
# First, try the same methodology as in the
# original [schaefer_pankratz_2018:26] paper:
# 1. Create contingency table:
# n2_num (Sg vs. Pl) x n1_pl_marker (zero vs. pluralic linker).
# 2. Perform chi-squared test of independence over the table
# to assess the statistical significance of the association between
# the Pl form of N2 and the presence of a pluralic linker in N1.
# 3. Perform the Cramer's V test to assess the strength
# of the association.
# 4. Inspect symmetrical standardized residuals to identify
# the cells that contribute to the association, and in which direction.

# create contingency table replicating [schaefer_pankratz_2018:26]
ic_alt_nipe_sg_l_ct = ic_alt_nipe_sg_l_sum \
    .groupby(level=1)[["l_sg", "l_pl"]].sum()   \
    .T  \
    # [["num_sg", "num_pl"]]
ic_alt_nipe_sg_l_ct.to_csv(
    os.path.join(res_outdir, "ic_alt_nipe_sg_l/contingency_table.tsv"),
    **outcsv_args
)
ic_alt_nipe_sg_l_ct

# %%
ic_alt_nipe_sg_l_ct.values.sum()

# %%
# even though I didn't find the original R code
# of [schaefer_pankratz_2018] for this experiment,
# the `chi2_contingency` function from `scipy.stats`
# produced the same results as in the paper
# on the same contingency table, so we can be
# confident that we are replicating the same analysis
chi2_res = chi2_contingency(ic_alt_nipe_sg_l_ct)

# the original R code for Cramer's V is available in
# linkingelements/Data/R/functions.R, and is as follows:
# 
#   cramer.v <- function(chisq) {
#       unname(sqrt(chisq$statistic/(sum(chisq$observed)*min(dim(chisq$observed)-1))))
#   }
#
# we will reconstruct it in Python:
#   dim(chisq$observed) -> ic_alt_nipe_sg_l_ct.shape
#
#   min(dim(chisq$observed)-1) -> min(
#       ic_alt_nipe_sg_l_ct.shape[0] - 1,
#       ic_alt_nipe_sg_l_ct.shape[1] - 1
#   )
# 
#   sum(chisq$observed) -> ic_alt_nipe_sg_l_ct.values.sum()
#
#   unname -> [irrelevant for Python]
def cramer_v(chi2: float, contingency_table: pd.DataFrame) -> float:
    return math.sqrt(
        chi2 / (
            contingency_table.values.sum() *
            min(
                contingency_table.shape[0] - 1,
                contingency_table.shape[1] - 1
            )
        )
    )

cramer_v_val = cramer_v(chi2_res.statistic, ic_alt_nipe_sg_l_ct)

# the original R code for Cohen's W is available in
# linkingelements/Data/R/functions.R, and is as follows:
# 
#   # cohen.w <- function(chisq) {
#       cramer.v(chisq) * sqrt(min(dim(chisq$observed)-1))
#   }
def cohen_w(cramer_v: float, contingency_table: pd.DataFrame) -> float:
    return cramer_v * math.sqrt(
        min(
            contingency_table.shape[0] - 1,
            contingency_table.shape[1] - 1
        )
    )

cohen_w_val = cohen_w(cramer_v_val, ic_alt_nipe_sg_l_ct)

ic_alt_nipe_sg_l_chi2 = pd.Series(
    data={
        "chi2": chi2_res.statistic.round(3),
        "df": chi2_res.dof,
        # = 1.9e-09, significant
        "p": chi2_res.pvalue,#.round(3),
        # = 0.172, small to medium effect size,
        # see ???
        "cramer_v": round(cramer_v_val, 3),
        # = 0.172, small to medium effect size,
        # see [cohen_1998:224-225]
        "cohen_w": round(cohen_w_val, 3)
    }
)

ic_alt_nipe_sg_l_chi2.to_csv(
    os.path.join(res_outdir, "ic_alt_nipe_sg_l/chi2.tsv"),
    **{**outcsv_args, "header": False}
)

ic_alt_nipe_sg_l_chi2

# %%
# even though I didn't find the original R code
# of [schaefer_pankratz_2018] for this experiment,
# the `standardized_resids` property of
# `statsmodels.stats.contingency_tables.Table`
# produced the same results as in the paper
# on the same contingency table, so we can be
# confident that we are replicating the same analysis
ic_alt_nipe_sg_l_resids = Table(ic_alt_nipe_sg_l_ct)    \
    .standardized_resids.round(3)
ic_alt_nipe_sg_l_resids.to_csv(
    os.path.join(res_outdir, "ic_alt_nipe_sg_l/resids.tsv"),
    **outcsv_args
)
# -6.069 for opposite number-linker: Pl vs non-pluralic and Sg vs pluralic
# 6.069 for congruent number-linker: Pl vs pluralic and Sg vs non-pluralic
# => 
ic_alt_nipe_sg_l_resids


