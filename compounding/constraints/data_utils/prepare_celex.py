# Even though AWK files are in general much more efficient than Python scripts for text processing tasks,
# we choose to implement this data preparation script in Python for several reasons:
# 1. Complexity of preprocessing: many files are involved simultaneously,
#    which would make the AWK code quite convoluted and hard to maintain.
# 2. Readability and maintainability: Python code is often more readable and easier to maintain than AWK code,
#    especially for complex tasks.
# 3. Personal competence in Python, hence, faster development cycle and more reliable code.

import os
import re
import pandas as pd
from phonecodes import phonecodes
from itertools import product
from typing import Literal, Optional


def main():

    # In preparing the CELEX data for our compounding constraints, we need to extract the following data
    # for all the non-compound nouns:
    # 1. Lemma.
    # 2. Morphological information: to retrieve gender, GenSg form, NomPl form; the latter two are needed
    #   to determine the inflectional class of the noun. Used in morphological constraints.
    # 3. Morphemic structure: to identify prefixes and suffixes. Used in derivational constraints.
    # 4. Derivational information: to identify base stems of derived nouns to be able to identify
    #   deverbal/deadjective/etc. nouns. Used in derivational constraints.
    # 5. Phonological information: to identify the final segment(s) of the noun. Used in phonological constraints.
    # 6. Syllabic structure: to identify monosyllabic vs. polysyllabic nouns as well as phonological quality of the noun.
    #   Used in phonological constraints.
    # 7. Frequency information.
    # Semantic and lexical properties are not contained in the CELEX data, so we do not extract them here.


    # To extract all the nencessary data, we need to parse the following files (see more about the files in
    # resources/Celex/german/gml/README):
    # 1. `gml.cd`: 'German Morphology, Lemmas'. This file contains lemmas, their POS, their derivational information and,
    #   hence, morphemic structure. We will only extract non-compound nouns.
    # 2. `gsl.cd`: 'German Syntax, Lemmas'. This file contains gender information for the lemmas.
    # 3. `gmw.cd`: 'German Morphology, Wordforms'. This file contains the inflected forms of the lemmas,
    #   one row per inflected form. We will extract the GenSg and NomPl forms of the nouns from here and will map
    #   them to the lemmas in `gml.cd` via lemma ids.
    # 4. `gpl.cd`: 'German Phonology, Lemmas'. This file contains phonological and syllabic information
    #   for the lemmas.
    # 5. `gfl.cd`: 'German Frequency, Lemmas'. This file contains frequency information for the lemmas.


    # To summarize:
    # 1. Lemma.                             `gml.cd`
    # 2. Morphological information.         POS: `gml.cd` (derived, alternatively: `gsl.cd`),
    #                                       gender: `gsl.cd` , paradigm: `gmw.cd` (derived)
    # 3. Morphemic structure.               `gml.cd`
    # 4. Derivational information.          `gml.cd`
    # 5. Phonological information.          `gpl.cd`
    # 6. Syllabic structure.                `gpl.cd`
    # 7. Frequency information.             `gfl.cd`

    celex_path = "resources/Celex/german"
    outpath = "resources/custom/compounding/intermediate_data"
    os.makedirs(outpath, exist_ok=True)

    # We will proceed as follows:
    # 1. Parse `gml.cd`.
    # 2. Parse `gmw.cd`. Here, it will be needed to
    # unparse lexicalized F(lexion) stems in `gml.cd` 
    # but later we will also extract GenSg and NomPl forms from here
    # (see step 6).
    # 3. Filter `gml.cd` for non-derivative nouns.
    # 4. Parse `gsl.cd`.
    # 5. Join `gml.cd` and `gsl.cd` on lemma id.
    # 6. Filter `gmw.cd` for GenSg and NomPl forms of the nouns
    #   in the filtered joint table from step 5.
    # 7. Join the filtered `gmw.cd` table to the filtered
    #   joint table from step 6 on lemma id.
    # 8. Parse `gpl.cd`.
    # 9. Filter `gpl.cd` for phonological and syllabic information
    #   of the nouns in the table from step 7. Convert phonological
    #   and notations into IPA.
    # 10. Join the filtered `gpl.cd` table to the table from step 7 on lemma id.
    # 11. Parse `gfl.cd`.
    # 12. Filter `gfl.cd` for frequency information of the nouns
    #   in the table from step 10.
    # 13. Join the filtered `gfl.cd` table to the table from step 10 on lemma id.
    # 14. Final processing: filter out lemmas with frequency below a certain threshold,
    #   filter out weak masculine nouns,
    #   conduct orthographic transformations (umlauts, lowering) etc.
    # 15. Save the final table as TSV.

    # Note: intermediate tables are to be filtered at each step
    # by suitable criteria.


    # 1. We start by parsing `gml.cd`. For reference, see the CELEX documentation
    # (5-54, 5-55, 5-63, 5-64, 5-70) and `gml/README`.

    # The following columns are relevant:
    # * Column 1: Lemma id.
    # * Column 2: Lemma.
    # * !Column 4 (disregarded): Specifies the compositional status of the lemma (simlex, derivative, compound);
    #   disregarded since it assigns both derivatives and compounds as 'complex' (C),
    #   while we only want to exclude compounds but non simple derivatives. Instead, we will infer the POS from
    #   the derivational information in Column (see below).
    # * !Columns 9 (disregarded): Morphemic structure. If both columns 9 and 24 are given, they correspond to different 
    #   possible analyses of the morphemic structure (primary in column 9, secondary in column 24.,
    #   in which case we will choose the primary analysis in column 9. Disregarded since for derivatives,
    #   it provides only the last-step morphemic structure (e.g. `abbau` instead of `ab-bau` for 'Abbau').
    #   Instead, we will infer morphemic structure from column 14 (see below).
    # * !Column 10 (disregarded): Morphemic schema. As opposed to the morphemic structure in column 9, this column
    #   provides a more abstract schema of the morphemic structure and maps morphemes from there
    #   to their types: stem/affix, if stem: noun/verb/adj/etc. Since we only need non-compound nouns,
    #   we will filter out all entries that have more than one stem in this column (stem markers are capitalized).
    #   Note though that we will not filter out entries that do not have a noun stem in their morphemic schema,
    #   since there are nouns derived from e.g. verbs or adjectives: e.g. 'Tiefe' has code `Ax` (Adj stem + affix).
    #   Disregarded since it is linked to the morphemic structure from column 9, hence, to a partial analysis.
    #   Instead, we will infer morphemic schema from column 14 (see below).
    # * Columns 14: POS and derivational information. Will be used to infer morphemic structure and morphemic schema.
    # * !Column 19 (disregarded): Code for the inflectional class of the noun. Disregarded because:
    #   1. we couldn't find the documentation about the codes in the CELEX guide, and
    #   2. for some nouns the code is missing.
    #   Hence, we will extracting the GenSg and NomPl forms directly from `gmw.cd`.

    gml = pd.read_csv(
        os.path.join(celex_path, "gml/gml.cd"),
        sep="\\",
        header=None,
        dtype=str,
        usecols=[0, 1, 13],
        names=["id", "lemma", "drvt_history"],
        index_col="id",
        keep_default_na=False,
        na_values=[""]  # prevent N+Adj morphemic schemas from being read as NaN
    )

    # drop records with any missing fields
    gml = gml.dropna()

    # infer morphemic structure and morphemic schema from column 14
    def _parse_morphemic_structure_schema(drv_steps: str) -> tuple:

        morphemic_structure = []
        morphemic_schema = ""

        # Derivational history is recursively built as H = (H1, H2, ...)[POS],
        # where each Hi is also of form H1 = (H11, H21, ...)[POS].
        # However, since we are not interested (for now) in specific derivational steps
        # and their hierarchy, we only need to extract the high-level POS
        # and all low-level <morpheme-type> information.
        pos = re.search(r"\[(?P<pos>[A-Z|.]+)\]$", drv_steps).group("pos")
        for match in re.finditer(r"\((?P<m>[^()]+)\)\[(?P<t>[A-Za-z|.]+)\]", drv_steps):
            morpheme = match.group("m")
            m_type = match.group("t")
            if not morpheme or not m_type:
                # return None if anything is missing (e.g. `((Berg)[N],(mann)[])[N]`)
                return None, None, None
            m_type = "x" if "|" in m_type else m_type  # affixes ("x") are marked as "Xout|.Xin"
            morphemic_structure.append(morpheme)
            morphemic_schema += m_type

        return "-".join(morphemic_structure), morphemic_schema, pos
    
    # We will filter for nouns later, for now we need 
    # all the analyses to be able to unparse lexicalized F(lexion) stems.
    gml["morphemic_structure"], gml["morphemic_schema"], gml["pos"] = zip(
            *gml["drvt_history"].apply(
                lambda x: _parse_morphemic_structure_schema(x)
        )
    )

    # drop records with any missing fields repeatedly
    gml = gml.dropna()

    # we can now drop the original `drvt_history` column
    gml = gml.drop(columns=["drvt_history"])


    # 2. Next, we parse `gmw.cd`. For reference, see the CELEX documentation
    # (5-83) and `gmw/README`. As of now, it will be needed to
    # unparse lexicalized F(lexion) stems in `gml.cd` 
    # but later we will also extract GenSg and NomPl forms from here.

    # The following columns are relevant:
    # * Column 2: Wordform.
    # * Column 3: Wordform count in Mannheim corpus (6M tokens);
    #   not needed per se, but will be used to resolve conflicts
    #   if the same wordform has multiple variants: 
    #   e.g. 'Mann' has variants 'Mannen' (wc: 5) vs 'Männer' (wc: 989).
    # * Column 4: Lemma id.
    # * Column 5: Paradigm codes (to identify GenSg and NomPl forms).

    gmw = pd.read_csv(
        os.path.join(celex_path, "gmw/gmw.cd"),
        sep="\\",
        header=None,
        dtype=str,
        usecols=[1, 2, 3, 4],
        names=["wordform", "freq", "id", "paradigm_code"],
        index_col="id"
    )

    # drop records with any missing fields
    gmw = gmw.dropna()


    # 3. Filter `gml.cd` for non-complex nouns.

    # First, filter out all records that have more than
    # one stem in their morphemic schema; allow only
    # A(dj), V(erb), N(oun) stems and affixes (x) as well as
    # P(reposition)s, which are in fact affixes as in 'mit-Glied'
    # or 'durch-Schnitt', and adverbs (B), for which the same holds,
    # e.g. 'fort-setzen' or 'hinter-bleiben'.
    # Additionally, allow lexicalized F(lexion) which
    # are in fact deverbatives ('Essen', 'Abfahrt', etc.)
    # and deadjectives ('Arme' etc.)
    # and R(oot)s which are in fact morphoids
    # (mostly of Greek and Latin origin) such as 
    # 'amortis' in 'Amortisation' or 'simul' in 'Simulator'.
    # For more information on the codes, see
    # the CELEX documentation (5-63).
    gml = gml[
        gml["morphemic_schema"].apply(
            lambda x: re.match(r"^[xPB]*[AVNFR][xPB]*$", x) is not None
        )
    ]

    # Now, lexicalized F(lexion) stems are stored in CELEX
    # with no analysis: they are underspecified by their
    # derivational history (deverbal or deadjectival) and
    # morphemic structure (e.g. no prefixes are indicated);
    # because of that, we need to unparse them separately
    # based on their respective lemmas.

    # explicitly add lemma column for easier lookups later
    gmw = gmw.join(gml["lemma"], on="id", how="inner")

    def _unparse_simple(row: pd.Series) -> tuple[str, str]:
        return row["morphemic_structure"], row["morphemic_schema"]
    
    def _unparse_inf(row: pd.Series) -> tuple[str, str]:
        # add infinitive suffix -en for infinitives
        # as CELEX does not include it
        morph_struct, morph_schema = _unparse_simple(row)
        return (
            # here, we don't actually care about allomorphy
            morph_struct + "-en",
            morph_schema + "x"
        )
    
    _test_vcodes = lambda targets, vcodes: any(
        re.search(target, vcodes) for target in targets
    )

    def _unparse_deverb(
        row: pd.Series,
        f_lemma: str,
        par_codes_str: str
    ) -> tuple[str, str]:
        
        # here, there are several possibilities for
        # derivational suffixes based on the paradigm codes;
        # note that errors are possible due to underanalyses,
        # e.g. 'reformierte' is analyzed as 'reformierte' `13SIA,13SKA`,
        # hence, 'reformier-te' instead of 'reformier-t-e', because
        # its correct analysis 'reformierte' `o4` is previously
        # removed because it points to a record in `gml.cd` with missing fields
        
        morph_struct, morph_schema = _unparse_simple(row)
        
        if _test_vcodes(["1SIE", "[13]{1,2}SKE", "rS"], par_codes_str):
            # 1PersSg of present tense indicative, ImpSg,
            # and 1/3PersSg of subjunctive present get -e suffix
            # e.g. 'wasche'
            marker = "-e"
            # however, 1PersSg of modal verbs is 0
            # e.g. 'be-darf'
            if (
                "1SIE" in par_codes_str
                and row["morphemic_structure"].split("-")[-1] in [
                    "duerf", "moeg", "koenn",
                    "muess", "woll", "wiss",
                    "soll", "sei"
                ]
            ):
                marker = ""
            # imperatives of strong verbs usually have 0 ending,
            # e.g. 'stich', 'tritt'
            elif (
                "rS" in par_codes_str
                and not f_lemma.endswith("e")
            ):
                marker = ""

        elif _test_vcodes(["2S[IK][EA]"], par_codes_str):
            # 2Sg of any tense and mood gets -st suffix,
            # with additional markers depending on tense and mood
            if "KE" in par_codes_str:
                # add a KI -e marker
                add_marker = "-e"
            elif "IA" in par_codes_str:
                # add a past tense -te marker
                # unless strong verb with 0
                add_marker = "-te"
                if not f_lemma.endswith("test"):
                    # strong verb with 0 ending
                    add_marker = ""
            elif "KA" in par_codes_str:
                # add a subjunctive past -te marker
                # unless strong verb with -e
                add_marker = "-te"
                if not f_lemma.endswith("test"):
                    # strong verb with -e
                    add_marker = "-e"
            else:
                # present
                add_marker = ""
            # always add -st for 2Sg of any tense and mood
            marker = add_marker + "-st"

        elif _test_vcodes(["[13]{1,2}S[IK]A"], par_codes_str):
            # 1/3PersSg get -te suffix in past of any mood
            marker = "-te"
            # however, 1/3PersSg of strong verbs is 0 / -e
            # in past tense indicative / subjunctive respectively
            if (
                "IA" in par_codes_str
                and not f_lemma.endswith("te")
            ):
                marker = ""
            elif (
                "KA" in par_codes_str
                and not f_lemma.endswith("te")
            ):
                marker = "-e"

        elif _test_vcodes(["3SIE", "2P[IK][EA]", "rP"], par_codes_str):
            # 3PersSg of indicative present, 2PersPl of in any tense and mood,
            # and ImpPl get -t suffix with additional markers
            # depending on tense and mood
            if "KE" in par_codes_str:
                # add a KI -e marker
                add_marker = "-e"
            elif "IA" in par_codes_str:
                # add a past tense -te marker
                # unless strong verb with 0
                add_marker = "-te"
                if not f_lemma.endswith("tet"):
                    # strong verb with 0 ending
                    add_marker = ""
            elif "KA" in par_codes_str:
                # add a subjunctive past -te marker
                # unless strong verb with -e
                add_marker = "-te"
                if not f_lemma.endswith("tet"):
                    # strong verb with -e
                    add_marker = "-e"
            else:
                # present or imperative
                add_marker = ""
            marker = add_marker + "-t"
            # however, 3PersSg of modal verbs
            # and strong verbs ending in -t is 0
            if (
                "3SIE" in par_codes_str
                and
                (
                    row["morphemic_structure"].split("-")[-1] in [
                        "duerf", "moeg", "koenn",
                        "muess", "woll", "wiss",
                        "soll", "sei"
                    ]
                    or (
                        row["lemma"].endswith("t")
                        and not f_lemma.endswith("et")
                    )
                )
            ):
                marker = ""

        elif _test_vcodes(["[13]{1,3}P[IK][EA]"], par_codes_str):
            # 1/3PersPl of any tense and mood get -en suffix,
            # with additional markers depending on tense and mood
            if "KE" in par_codes_str:
                # add a KI -e marker;
                # not used since -e and -en
                # merge into -en so 13PIE and 13PKE 
                # are indistinguishable
                add_marker = "" # "-e"
            elif "IA" in par_codes_str or "KA" in par_codes_str:
                # add a past tense -te marker
                # unless strong verb with 0 / -e
                # indicative / subjunctive respectively;
                # the -e option is not used since -te and -en
                # merge into -ten so 13PIA and 13PKA
                # are indistinguishable
                add_marker = "-te"
                if not f_lemma.endswith("ten"):
                    # strong verb with 0 ending
                    add_marker = "" # "-e", ignored (see above)
            else:
                # present
                add_marker = ""
            marker = add_marker + "-en"

        else:
            
            return None, None  # unrecognized paradigm codes
        
        return (
            # here, we don't actually care about allomorphy
            morph_struct + marker,
            morph_schema + "x" * marker.count("-")
        )

    def _get_adj_flexion(inflect_code: str) -> str:
        # carried out into a separate function
        # because it is shared between
        # deadjectives and lexicalized participles
        # such as 'abgeordnet-e'
        match inflect_code:
            case "0":
                return ""
            case "4":
                return "-e"
            case "5":
                return "-en"
            case "6":
                return "-er"
            case "7":
                return "-em"
            case ["8", "9"]:
                return "-s"
        return ""
            
    def _unparse_p2(
        row: pd.Series,
        f_lemma: str,
        inflect_code: Optional[str]="0"
    ) -> tuple[str, str]:
        morph_struct, morph_schema = _unparse_simple(row)
        # Partizip II, return verb's morphemic structure/schema
        # plus PII -t/-en suffix (CELEX does not include the inf -en)
        # and PII ge- prefix if applicable;
        # here, we don't actually care about allomorphy
        part_marker = "-t" if f_lemma.endswith("t") else "-en"
        # place ge- right before stem if needed:
        # 'ge-mach', 'ein-ge-stell', 'her-vor-ge-bring';
        # note though that inaccuracies might occur
        # due to occasional incorrect morphemic structures in CELEX,
        # e.g. 'angestrengt' is analyzed as 'anstreng' instead of 'an-streng'
        # so the output of this function will be
        # 'ge-anstreng-t' instead of 'an-ge-streng-t'
        morphemes = morph_struct.split("-")
        # since stem might be trailed by suffixes
        # (e.g. 'angeschuldigt' from lemma 'an-Schuld-ig xNx'),
        # find the position of the base stem;
        # only records with a single A/V/N/F/R stems were kept
        # (and F cannot appear here because of the condition
        # in `_maybe_unparse_and_postprocess`)
        base_stem_ind = re.search(r"[AVNR]", morph_schema).start()
        prefixes = ''.join(morphemes[:base_stem_ind])
        if f_lemma.startswith(prefixes + "ge"):
            # ge- prefix in PII
            morphemes.insert(base_stem_ind, "ge")
            morph_struct = "-".join(morphemes)
            # even if there are other prefixes, morphemic schema
            # encodes all of them as 'x'
            morph_schema = "x" + morph_schema
        inflect_marker = _get_adj_flexion(inflect_code)
        return (
            morph_struct + part_marker + inflect_marker,
            morph_schema + "x" + "x" * bool(inflect_marker)
        )

    def _unparse_p1(
        row: pd.Series,
        inflect_code: Optional[str]="0"
    ) -> tuple[str, str]:
        morph_struct, morph_schema = _unparse_simple(row)
        inflect_marker = _get_adj_flexion(inflect_code)
        return (
            # here, we don't actually care about allomorphy
            morph_struct + "-end" + inflect_marker,
            morph_schema + "x" + "x" * bool(inflect_marker)
        )

    def _unparse_deadj(row: pd.Series, par_code: str) -> tuple[str, str]:
        morph_struct, morph_schema = _unparse_simple(row)
        comp_degree, inflect_code = par_code
        comparative_marker = (
            "" if comp_degree == "o" else
            "-er" if comp_degree == "c" else "-st"
        )
        inflect_marker = _get_adj_flexion(inflect_code)
        # here, we don't actually care about allomorphy
        return (
            morph_struct + comparative_marker + inflect_marker,
            morph_schema + "x" * (
                comparative_marker + inflect_marker
            ).count("-")
        )

    _unparsers = {
        "inf": _unparse_inf,
        "deverb": _unparse_deverb,
        "p2": _unparse_p2,
        "p1": _unparse_p1,
        "deadj": _unparse_deadj
    }

    def _unparse_and_postprocess(
        row: pd.Series,
        postprocess: Optional[Literal["", "inf", "deverb", "p2", "p1", "adj", "cmpr", "sprl"]]="",
        **postprocessing_kwargs
    ) -> tuple[str, str]:
        if not postprocess:
            if row["pos"] == "V":
                # lemma 'V' is always infinitive;
                # add infinitive suffix -en for infinitives
                # as CELEX does not include it
                output = _unparse_inf(row)
            else:
                output = _unparse_simple(row)
        else:
            output = _unparsers[postprocess](row, **postprocessing_kwargs)
        return output

    def _maybe_unparse_and_postprocess(
        base_lemma: str,
        gml: pd.DataFrame,
        cache: dict,
        postprocess: Optional[Literal["", "inf", "deverb", "p2", "p1", "adj", "cmpr", "sprl"]]="",
        **postprocessing_kwargs
    ) -> tuple:
        # if in cache, return cached value,
        # otherwise, look up, analyze, and cache
        if base_lemma in cache:
            return cache[base_lemma]
        # Since in morphemic structures of CELEX entries,
        # stems are specified without their respective lemma ids,
        # we can only rely on lemmas themselves to look up these stems.
        # Thus, both no entries and multiple entries for the same lemma
        # are unreliable for us. The only difference is though,
        # that if there are no lemmas for a lexicalized stem,
        # there is still a chance to unparse it by looking it up
        # as a wordform and not as a lemma (scenario 2) whereas 
        # if there are multiple lemmas for the same lexicalized stem,
        # there is no way to disambiguate them (scenario 0).
        f_lemma_entries = gml[
            (gml["lemma"] == base_lemma) &
            # we ignore lexicalized lemmas as they 
            # are always underspecified
            (gml["morphemic_schema"] != "F")
        ]
        if not len(f_lemma_entries):
            # route for scenario 2
            return False, True # (not found, try as wordform)
        elif len(f_lemma_entries) == 1:
            return _unparse_and_postprocess(
                f_lemma_entries.iloc[0],
                postprocess=postprocess,
                **postprocessing_kwargs
            )
        else:
            # There are many cases in which there are multiple
            # variants of the same lemma with omonymous morphemes.
            # These are mostly (if not always) verbs with omonymous
            # prefixes that produce differentces in morphological
            # paradigm, e.g. 'überlegen' -- 'überlegt' vs
            # 'überlegen' -- 'übergelegt' for 'Überlegenheit'. 
            # In cases where such verbs are used as bases
            # for lexicalized F(lexion) nouns, original differences
            # in their morphological paradigms do not matter since the
            # derivates are nouns that receive a new paradigm anyway.
            # That said, if there are multiple options of the base
            # word for a lexicalized F(lexion) noun, as long as
            # they have the same morphemic structure and schema,
            # we can safely take one of them.
            # Cases when omonimous base words with the same
            # morphemic properties respectively yield omonimous
            # derivates will be dealt with at the final filtering stage.
            if (
                len(pd.unique(f_lemma_entries["morphemic_structure"])) == 1
                and len(pd.unique(f_lemma_entries["morphemic_schema"])) == 1
            ):
                # might have joint the condition with the previous one
                # but for readability kept it separate
                output = _unparse_and_postprocess(
                    f_lemma_entries.iloc[0],
                    postprocess=postprocess,
                    **postprocessing_kwargs
                )
                cache[base_lemma] = output
                return output
            else:
                return False, False # (ambiguous, do not try)
            
    def _resolve_lexicalized_flexion(
        row: pd.Series,
        gml: pd.DataFrame,
        cache: dict,
        f_lemma: str
    ):
        
        base_lemma = row["lemma"]
        bf_lemmas = f"{base_lemma}|{f_lemma}"
        # not using only F lemma here because in case of lexicalized
        # flexion duplicates, its base lemma coincides
        # with the F lemma and so when the correct duplicate
        # comes, None will be found in cache even though 
        # this time the base lemma is correct:
        # e.g. 'besser' `o0` has base lemma 'besser' (lexicalized 
        # duplicate), so correct analysis 'besser' `c0` 'gut'
        # also returs None if we use F lemma here;
        # using only base lemma is not reliable either
        # since there might be multiple F lemmas
        # derived from the same base lemma;
        # hence, we use both base and F lemmas here
        if bf_lemmas in cache:
            return cache[bf_lemmas]
        
        # For scenario 2, CELEX is not very consistent either;
        # however, it is possible un unravel the structure
        # of most of the stems based on their inflected form codes
        # (see more in the CELEX documentation, 5-84).
        # we have fornd the following possibilities for scenario 2:
        #
        # 1. Deverbal nouns:
        #
        #   1.1. Converted deverbals: have a code `i` and (almost)
        #       always are also followed by codes `13PIE` and `13PKE`:
        #       plural indicative or conjunctive of 1 or 3 person:
        #       'glauben', 'kommen' etc.
        #       In principal, they should not eventually be analyzed
        #       here as most (if not all) of them have a full analysis
        #       in `gml.cd` (scenario 1); however, we add a fallback
        #       here just in case: we return the verb's morphemic
        #       structure/schema plus -en infinitive (alternatively: conversion)
        #       suffix as CELEX does not include it.
        #
        #   1.2. Derived deverbals; for some reason, CELEX
        #       wants to analyze such stems as verbal forms and so
        #       they are recognizable by corresponding verbform codes:
        #       'abfahrt' `2PIE`, 'abschnitt' `13SIA`,
        #       'bedarf' `1SIE,3SIE` (why not `13SIE`?),
        #       'beitritt' `3SIE`, 'umfrage' and 'vorhersage' `1SIE,13SKE`,
        #       'wasche' `1SIE,13SKE,rS`, and much more. In this case,
        #       we look up the morphemic structure/schema of the 
        #       original verb stem and return it plus whatever
        #       explicit suffix is used (e.g. 0 for 'Abfahrt',
        #       -e for 'wasche', etc.).
        #
        # 2. Participles:
        #
        #   2.1. Partizip II forms: have code `pA`:
        #       e.g. 'abgeklaert', 'versandt' etc.;
        #       in case of strong verbs whose PII form
        #       is identical to their infinitive, are followed
        #       by `13PIE`, `13PKE`, and `i` codes:
        #       'entkommen', 'erlesen'.
        #       In this case, we look up the morphemic structure/schema
        #       of the original verb stem and modify it
        #       to add PII suffix -t/-en and PII prefix ge- if applicable.
        #       In the latter case, they are indistinguishable
        #       from converted deverbals (see 1.1 above)
        #       and must have a full analysis in `gml.cd`.
        #       Even if otherwise, no additional fallback 
        #       is required since the general unparsing function
        #       for participles already handles this case.
        #
        #   2.2. Partizip I forms: have code `pE`:
        #       e.g. 'stehend', 'laufend' etc.
        #       In this case, we look up the morphemic structure/schema
        #       of the original verb stem and modify it
        #       to add PI suffix -end.
        #
        # 3. Deadjectival nouns:
        #
        #   3.1. Weak deadjectival nouns: have code `oN`, where
        #       N is a digit coding the inflexional suffix:
        #       e.g. 'kitzelig' `o0`, 'arme' `o4`, 'liegendem' `o7` etc.
        #       Both adjectives and any participles can
        #       be the base of such nouns. In first case,
        #       we look up the morphemic structure/schema
        #       of the original adjective stem and modify it
        #       inflextional suffix with respect to the `oN` code (mostly -e).
        #       In second case, we need to pass the participle
        #       through the participle unparsing function. 
        #
        #   3.2. Comparative adjective forms: have code `cN`, where
        #       N is a digit (mostly 0) coding the inflexional suffix:
        #       e.g. 'besser' `c0`, 'kritischere' `c4`, 'exklusiverem' `c7` etc.
        #       In this case, we look up the morphemic structure/schema
        #       of the original adjective stem and modify it
        #       to add comparative suffix -er and inflextional suffix
        #       with respect to the `cN` code (mostly zero).
        #
        #   3.3. Superlative adjective forms: have code `uN`, where
        #       N is a digit (mostly 0) coding the inflexional suffix:
        #       e.g. 'best' `u0`, 'bestimmtste' `u4`, 'suessestem' `u7` etc.
        #       In this case, we look up the morphemic structure/schema
        #       of the original adjective stem and modify it
        #       to add comparative suffix -st and inflextional suffix
        #       with respect to the `uN` code (mostly zero).
        #
        # From verbal forms, infinitives, pA, and pE are the simplest to unparse
        # since they only have one-two scenarios to unparse each;
        # derived deverbals deverbals are much more complicated since
        # there are many different verb forms that can be bases
        # for such nouns and their respective suffixes.
        # In cases of syncretism between the two groups
        # (e.g. 'belächelt' `3SIE,2PIE,2PKE,rP,pA`),
        # it is much more efficient to unparse it by scenario
        # of the first group rather that by scenario of derived deverbals.
        # Moreover, there is a fact that forces us to unparse
        # those even after deadjectival forms.
        # Almost all PIIs exist in `gwd.cd` as `pA` of a verb and
        # as a `o0` of the PII itself; it becomes critical
        # when the `oX` form of a PII coincides with one of the derived
        # deverbals. In this case, if we process the latter before deadjectivals,
        # we will get an incorrect morphemic structure/schema of a deverbal
        # rather than the correct one of a PII. For example,
        # 'reformierte' exists as 'reformierte' `o4` that lead us to
        # 'reformiert' `o0` that leads us to 'reformiert' `3SIE,2PIE,rP,pA`
        # which results in correct `re-form-ier-t-e xRxxx`. Instead,
        # if we processed derived deverbals first, we would first catch
        # 'reformierte' as 'reformiert' `13SIA,13SKA`, which would result
        # in incorrect `re-form-ier-te xRxx`.
        # 
        # Deadjectival nouns are otherwise mostly straightforward since
        # they appear independently (no mixture of verbal and adjectival
        # codes is observed) and there are only two cases of
        # syncretism: `06,c0` and `o0,o4` for adjectives ending with -e.
        # However, there is one edge case that forces us
        # to process weak deadjectival nouns before verbal forms.
        #
        # Thus, we will first try to unparse verbal forms
        # as infinitives, pA, or pE if possible, then
        # move to deadjectivals, and finally
        # try to unparse derived deverbals.

        # match the codes to the scenarios above
        lemma = row["lemma"]
        par_codes_str = row["paradigm_code"]
        par_codes = par_codes_str.split(",")

        args = (lemma, gml, cache)

        # 1.1. Converted deverbals
        # if there are other codes besides `i`, they are ignored
        # since the form can already be unparsed as infinitive
        if "i" in par_codes:
            # no changes needed
            morph_struct, morph_schema = _maybe_unparse_and_postprocess(
                *args, postprocess="inf"
            )

        # 2.1. Partizip II
        # if there are other codes besides `pA`, they are ignored
        # since the form can already be unparsed as PII
        elif "pA" in par_codes:
            # add PII suffix -t/-en and PII prefix ge- if applicable
            morph_struct, morph_schema = _maybe_unparse_and_postprocess(
                *args, postprocess="p2", f_lemma=f_lemma
            )

        # 2.2. Partizip I
        # pE always appears alone
        elif "pE" in par_codes:
            # add PI suffix -end
            morph_struct, morph_schema = _maybe_unparse_and_postprocess(
                *args, postprocess="p1"
            )

        # # 3.1. Weak deadjectival nouns
        # # 3.2. Comparative adjective forms
        # # 3.3. Superlative adjective forms
        elif re.search(r"[ocu]\d", par_codes_str):
            # in rare cases of syncretism
            # (`o0,o4` and `c0,06`),
            # it is in both cases easier to process
            # the first: `x0`
            par_code = par_codes[0]
            # for deadjectivals, we have two cases:
            # either these are real adjectives,
            # or participles used as adjectives,
            # in which case theses are duplicate entries
            # identical to the corresponding PII/PI forms
            # but marked as deadjectivals (e.g.
            # there is 'abgeklärt' `pA` and `o0`, same holds
            # for many of PIIs/PIs).
            # Because of that, we will first check if there is
            # an identical PII/PI form and if yes, we will
            # parse it insdead. Otherwise, we will parse
            # it as an adjective.
            possible_p2_forms = gmw[
                (gmw["wordform"] == lemma.lower())
                & (gmw["paradigm_code"].str.contains("pA"))
            ]
            possible_p1_forms = gmw[
                (gmw["wordform"] == lemma.lower())
                & (gmw["paradigm_code"].str.contains("pE"))
            ]
            if len(possible_p2_forms) == 1:
                # found the identical PII form,
                # parse it instead
                ident_p2_lemma = possible_p2_forms.iloc[0]["lemma"]
                # parse as PII
                morph_struct, morph_schema = _maybe_unparse_and_postprocess(
                    # in this case, the adjective stores the participle
                    # as its lemma as it's lexicalized
                    ident_p2_lemma, gml, cache, postprocess="p2",
                    f_lemma=lemma, inflect_code=par_code[1]
                )
            elif len(possible_p1_forms) == 1:
                # found the identical PI form,
                # parse it instead
                ident_p1_lemma = possible_p1_forms.iloc[0]["lemma"]
                # parse as PI
                morph_struct, morph_schema = _maybe_unparse_and_postprocess(
                    # in this case, the adjective stores the participle
                    # as its lemma as it's lexicalized
                    ident_p1_lemma, gml, cache, postprocess="p1",
                    inflect_code=par_code[1]
                )
            else:
                # add inflexional suffix if applicable, e.g. -e for 'abgeornete'
                morph_struct, morph_schema = _maybe_unparse_and_postprocess(
                    *args, postprocess="deadj", par_code=par_code
                )

        # 1.2. Derived deverbals
        # NB! must be checked the last (explanation above);
        # can consist of several codes,
        # each of them being either personal form:
        # person(s) (1/2/3) + number (S/P) + mood (I/K) + tense (E/A),
        # or imperative form: (r) + number (S/P)
        elif re.search(r"[123]{1,3}[SP][IK][EA]|(r[SP])", par_codes_str):
            # add derivative suffix if applicable, e.g. -e for 'Wasche'
            morph_struct, morph_schema = _maybe_unparse_and_postprocess(
                *args, postprocess="deverb", f_lemma=f_lemma, par_codes_str=par_codes_str
            )

        # scenario 3: no known/relevant analysis found
        else:
            morph_struct, morph_schema = None, None
        
        # now check for successful unparsing since
        # `_maybe_unparse_and_postprocess` might return
        # `(False, X)` if no or ambiguous analyses found,
        # e.g. `(False, True)` for `abgefeimt`;
        # in this case, both no and ambiguous analyses
        # lead to skipping the entry
        # (as opposed to initial lemma lookup where
        # we could try to look it up as a wordform)
        if morph_struct:
            output = (morph_struct, morph_schema)
        
        # scenario 3/0: none/ambiguous analyses found
        else:
            output = (None, None)

        cache[bf_lemmas] = output
        return output

    def _resolve_lexicalized_flexions(
        row: pd.Series,
        gml: pd.DataFrame,
        gmw: pd.DataFrame,
        cache: dict
    ) -> tuple[str, str]:
        
        # The variety of analyses of lexicalized F(lexion) stems in CELEX
        # is rather large, complicated, and unsystematic. Here, we provide
        # an empirical description of the observations that we will be
        # using to unparse them.
        #
        # There are four scenarios:
        # 0. Lexicalized F(lexion) noun is
        #   present `gml.cd` but multiple non-F analyses are provided.
        #   Impossible to disambiguate, unreliable, skip.
        # 1. Best case scenario: lexicalized F(lexion) noun is
        #   present as a separate lemma in `gml.cd`,
        #   and its full analysis is provided,
        #   e.g. 'Abzug' is analyzed as 'ab-zieh xV'.
        #   In this case we just take the morphemic structure/schema.
        #   Note though that in these cases the stems may be
        #   underanalyzed (e.g. 'Zugang' is analyzed as 'zugang N'),
        #   but in these cases that is the only available analysis.
        #   We unfortunately cannot identify such cases systematically,
        #   so we just take whatever analysis is provided. 
        # 2. No analysis is provided in `gml.cd` but `gmw.cd`
        #   contains a pointer to the original verb/adjective stem
        #   as well as its specific inflected form
        #   (NB! in this case the wordform in `gmw.cd` is lowercase),
        #   e.g. 'Abfahrt' is analyzed as 'Abfahrt F' in `gml.cd`,
        #   while `gmw.cd` has 'abfahrt 2PIE abfahren';
        #   e.g. 'Bekannte' is analyzed as 'Bekannte F' in `gml.cd`,
        #   while `gmw.cd` has 'bekannte o4 bekannt'.
        #   In this case, we look up the morphemic structure/schema
        #   of the original stem and modify it according to its specific
        #   inflected form (e.g. add suffix -er for comparatives).
        # 3. No analysis is provided in `gml.cd` and `gmw.cd`
        #   contains no or multiple analyses. Unreliable, skip.

        orig_morph_struct = row["morphemic_structure"]
        orig_morph_schema = row["morphemic_schema"]

        # first, all non-F entries are returned as is
        if row["pos"] != "N" or "F" not in orig_morph_schema:
            return orig_morph_struct, orig_morph_schema
        
        # identify the F itself
        orig_morphemes = orig_morph_struct.split("-")
        f_lemma_ind = orig_morph_schema.index("F")
        f_lemma = orig_morphemes[f_lemma_ind]
        
        # try for scenario 1: lexicalized F(lexion) noun is
        #   present as a separate lemma in `gml.cd`,
        #   and its full analysis is provided
        morph_struct, morph_schema = _maybe_unparse_and_postprocess(f_lemma, gml, cache)
        
        # it worked, scenario 1
        if morph_struct:
            output = (morph_struct, morph_schema)
        
        # scenario 0: ambiguous analyses found
        elif (not morph_struct) and (not morph_schema):
            output = (None, None)

        # try for scenario 2
        else:

            f_lemma = f_lemma.lower()
            f_lemma_forms = gmw[gmw["wordform"] == f_lemma]

            # scenario 3: no analyses found
            if not len(f_lemma_forms):
                output = (None, None)
            
            # scenario 2: analyses found
            elif len(f_lemma_forms) == 1: # simple case: only one analysis found

                f_lemma_info = f_lemma_forms.iloc[0]
                output = _resolve_lexicalized_flexion(
                    f_lemma_info, gml, cache, f_lemma
                )

            else:

                # most of the cases with multiple analyses
                # is due to the fact that many participles
                # exist both as `pA` and as its
                # lexicalized version as a deadjectival `oX`;
                # however, in order to make the processing
                # here simpler and more robust, we will
                # just unparse each of the analyses separately
                # and check if they all lead to the same output;
                # if yes, we take that output, otherwise skip;
                # it will also not be too much slower since
                # in case of the duplicates, the second time around
                # will be found in the cache
                morph_structs = set()
                morph_schemas = set()
                for _, f_lemma_info in f_lemma_forms.iterrows():
                    morph_struct, morph_schema = _resolve_lexicalized_flexion(
                        f_lemma_info, gml, cache, f_lemma
                    )
                    # either None, None, or actual values;
                    # ignoring None since most of lexicalized versions `oX`
                    # will returns Nones (e.g. 'besser' `o0` vs 'besser' `c0`
                    # or 'abgeklärt' `o0` vs 'abgeklärt' `pA`)
                    if morph_struct and morph_schema:
                        morph_structs.add(morph_struct)
                        morph_schemas.add(morph_schema)

                if len(morph_structs) == 1 and len(morph_schemas) == 1:
                    output = (
                        morph_structs.pop(),
                        morph_schemas.pop()
                    )
                else:
                    # abiguous, unreliable, skip
                    # e.g. 'abgewogen' is PII for both
                    # 'abwiegen' and 'abwägen'
                    output = (None, None)

        # finally, we need to replace the F in the
        # morphemic structure/schema of the original entry
        # with the resolved values if non Nones
        if output == (None, None):
            return None, None
        
        else:
            morph_struct, morph_schema = output
            # replace F with resolved values
            orig_morphemes[f_lemma_ind] = morph_struct # to be concatenated back
            new_morph_struct = "-".join(orig_morphemes)
            # always 1 F can be present
            new_morph_schema = orig_morph_schema.replace("F", morph_schema)
            return new_morph_struct, new_morph_schema

    _parsing_cache = {}
    gml["morphemic_structure"], gml["morphemic_schema"] = zip(
        *gml.apply(
            # pass gml and gmw for lookups
            lambda row: _resolve_lexicalized_flexions(row, gml, gmw, _parsing_cache),
            axis=1
        )
    )

    # drop records with any missing fields after
    gml = gml.dropna()

    # drop non-noun records
    gml = gml[gml["pos"] == "N"]
    # now we can drop the 'pos' column since we now have nouns only
    gml = gml.drop(columns=["pos"])


    # 4. Next, we parse `gsl.cd`. For reference, see the CELEX documentation
    # (5-87, 5-88) and `gsl/README`.

    # The following columns are relevant:
    # * Column 1: Lemma id.
    # * !Column 4 (disregarded): POS. Disregarded since we
    #   already infer POS from `gml.cd`.
    # * Column 5: Gender.

    gsl = pd.read_csv(
        os.path.join(celex_path, "gsl/gsl.cd"),
        sep="\\",
        header=None,
        dtype=str,
        usecols=[0, 4],
        names=["id", "gender"],
        index_col="id"
    )

    # drop records with any missing fields and remove duplicates
    gsl = gsl[~gsl.index.duplicated(keep="first")]
    gsl = gsl.dropna()


    # 5. We join `gml.cd` and `gsl.cd` on lemma id.
    gmsl = gml.join(gsl, how="inner")

    # we can also convert the gender codes to more readable values
    # (see CELEX documentation 5-88)
    gmsl["gender"] = gmsl["gender"].map(
        lambda x: "".join([{"1": "m", "2": "f", "3": "n"}[c] for c in x])
    )


    # 6. We filter `gmw.cd` for GenSg and NomPl forms of the nouns
    # in the filtered joint table from step 5.

    # remove wordforms of lemmas that are not in `gmsl`
    gmw = gmw[gmw.index.isin(gmsl.index.values)]

    # split records by `paradigm_code`; rewrites as one wordform per row, even if
    # multiple paradigm codes are assigned to the same wordform (e.g. Tiefe\nS,gS,dS,aS
    # will be rewritten as 4 rows: Tiefe\nS, Tiefe\gS, Tiefe\dS, Tiefe\aS)
    gmw = gmw.assign(paradigm_code=gmw["paradigm_code"].str.split(",")) # rewrites as list
    gmw = gmw.explode("paradigm_code")  # unscrambles into one entry per list item

    # keep only GenSg and NomPl forms
    gmw = gmw[gmw["paradigm_code"].isin(["gS", "nP"])]

    def _choose_higher_freq(group: pd.Series) -> str:
        if len(group) == 1:
            return group
        # if multiple variants exist, choose the one(s)
        # with higher frequency: all the variants that
        # have at least 50% of the winner's frequency
        group["freq"] = group["freq"].astype(int) + 1   # add-1 smoothing
        group["freq"] = group["freq"] / group["freq"].max()
        group = group[group["freq"] >= 0.5]
        # if still multiple variants,
        # concatenate them with a slash
        return group.groupby(level=0).agg({
            "wordform": lambda x: "/".join(x),
            "freq": "first",  # or "max", "mean", etc.
            "paradigm_code": "first"
        })
    
    # consolidate coexisting GenSg and NomPl forms
    # by their frequency; process consolidation separately
    # to avoid confusion when gS and nP are identical
    gmw_gs = gmw[gmw["paradigm_code"] == "gS"]
    gmw_gs_consolidated = gmw_gs.groupby(level=0)   \
                                .apply(_choose_higher_freq) \
                                .reset_index(level=1, drop=True)    \
                                .rename(columns={"wordform": "gen_sg"})

    gmw_np = gmw[gmw["paradigm_code"] == "nP"]
    gmw_np_consolidated = gmw_np.groupby(level=0)   \
                                .apply(_choose_higher_freq) \
                                .reset_index(level=1, drop=True)    \
                                .rename(columns={"wordform": "nom_pl"})
    
    # join GenSg and NomPl forms into one table with two respective columns;
    # join by left since missing plural forms are allowed
    gmw = gmw_gs_consolidated["gen_sg"].to_frame()  \
                                       .join(gmw_np_consolidated["nom_pl"], how="left")
 

    # 7. We join the filtered `gmw.cd` table to the filtered
    # joint table from step 6 on lemma id. For that, we need to
    # take each record in `gmsl` and attach the corresponding
    # GenSg and NomPl forms from `gmw`.
    gmslw = gmsl.join(gmw, how="inner")

    # drop records with missing GenSg forms; NomPl forms
    # can be missing for some nouns (e.g. mass or abstract nouns);
    # in particular, CELEX does not provide NomPl forms for many nouns
    # ending in -keit or -heit.
    gmslw = gmslw.dropna(subset=["gen_sg"])


    # 8. Parse `gpl.cd`. For reference, see the CELEX documentation
    # (5-28) and `gpl/README`.

    # The following columns are relevant:
    # * Column 1: Lemma id.
    # * Column 4: Phonetic transcription of the lemma in DISC notation,
    #   including syllable boundaries and stress marker. Since the latter
    #   are included, we do not need to parse syllabic structure separately.

    gpl = pd.read_csv(
        os.path.join(celex_path, "gpl/gpl.cd"),
        sep="\\",
        header=None,
        dtype=str,
        usecols=[0, 3],
        names=["id", "phonetic_transcription"],
        index_col="id"
    )

    # drop records with any missing fields
    gpl = gpl.dropna()


    # 9. We filter `gpl.cd` for phonological and syllabic information
    # of the nouns in the table from step 7. Convert phonological
    # and notations into SAMPA.

    # remove phonetic transcriptions of lemmas that are not in `gmslw`
    gpl = gpl[gpl.index.isin(gmslw.index.values)]

    # convert CELEX DISC notation into IPA
    gpl = gpl["phonetic_transcription"].apply(
        lambda x: phonecodes.convert(
            x,
            "disc",
            "ipa",
            language="deu"
        # for some reason maps German ʁ as r
        ).replace("r", "ʁ")
    )


    # 10. We join the filtered `gpl.cd` table to the table from step 7 on lemma id.
    gmsplw = gmslw.join(gpl, how="inner")

    
    # 11. Parse `gfl.cd`. For reference, see the CELEX documentation
    # (5-98) and `gfl/README`.

    # The following columns are relevant:
    # * Column 1: Lemma id.
    # * Column 7: Raw count (all wordforms of a lemma) in Mannheim corpus
    #   (6M tokens, 5.4M from written, and 0.6M from spoken texts).

    gfl = pd.read_csv(
        os.path.join(celex_path, "gfl/gfl.cd"),
        sep="\\",
        header=None,
        dtype=str,
        usecols=[0, 6],
        names=["id", "freq"],
        index_col="id"
    )

    # drop records with any missing fields
    gfl = gfl.dropna()


    # 12. We filter `gfl.cd` for frequency information of the nouns
    # in the table from step 10.

    gfl = gfl[gfl.index.isin(gmsplw.index.values)]


    # 13. We join the filtered `gfl.cd` table to the table from step 10 on lemma id.
    gmspflw = gmsplw.join(gfl, how="inner")


    # 14. Final processing: filter out lemmas with frequency below a certain threshold,
    # filter out weak masculine nouns,
    # conduct orthographic transformations (umlauts, lowering) etc.

    # freq check
    freq_threshold = 5
    gmspflw = gmspflw[gmspflw["freq"].astype(int) >= freq_threshold]

    # filter out weak masculine nouns
    # (those that form their GenSg and NomPl with -n or -en suffix)
    def _is_weak_masculine(row: pd.Series) -> bool:
        if row["gender"] != "m":
            return False
        lemma = row["lemma"]
        gen_vars = row["gen_sg"].split("/")
        plur_vars = row["nom_pl"].split("/") if pd.notna(row["nom_pl"]) else []
        marker = "n" if row["phonetic_transcription"][-1] == "@" else "en"
        return any(
            (gen_var == lemma + marker and plur_var == lemma + marker)
            for gen_var, plur_var in product(gen_vars, plur_vars)
        )
    
    gmspflw = gmspflw[~gmspflw.apply(_is_weak_masculine, axis=1)]

    # lower and apply orthographic transformations of umlauts;
    # return Nonefor missing Pl forms
    def umlambda(x: str) -> str:
        
        if pd.isna(x):
            return None
        
        x = x.lower()

        x = re.sub("(?<![aeiouy])ae", "ä", x)
        x = re.sub("(?<![aeiouy])oe", "ö", x)
        x = re.sub("(?<![aeiouy])ue", "ü", x)
        
        return x
    
    target_columns = ["lemma", "morphemic_structure", "gen_sg", "nom_pl"]
    gmspflw[target_columns] = gmspflw[target_columns].apply(
        lambda col: col.apply(umlambda)
    )

    # filter out one- and two-character lemmas except for
    # 'Ei', 'Öl', 'As' (they are otherwise letter names or interjections)
    gmspflw = (
        gmspflw[
            (gmspflw["lemma"].str.len() > 2) |
            (gmspflw["lemma"].isin(["ei", "öl", "as"]))
        ]
    )

    # final check: drop records with any missing fields except for `nom_pl`
    gmspflw = gmspflw.dropna(subset=list(set(gmspflw.columns) - {"nom_pl"}))

    # Since in GeCoDB, we can only rely on lemma string representations
    # (and not lemma ids) when retrieving any infos from CELEX,
    # we should drop all duplicate lemmas here to avoid ambiguities later on.
    # If an ambiguity arises, we don't want to just drop one of the entries
    # randomly, but rather drop all ambiguous entries altogether.
    # The reason for that is that most of such duplicates have different
    # morphologic paradigms (e.g. 'Band' -- 'Bande' and 'Band' -- 'Bands',
    # 'Bank' -- 'Bänke' and 'Bank' -- 'Banken', also 'Steuer', 'Leiter' etc.),
    # so running both semantic and morphologic constraints against such entries
    # would be unreliable.
    # Otherwise, in rare cases where the duplicates have all the same
    # properties, we keep one of them ('Mutter', 'Hahn', 'Gesicht').
    # TODO: disambiguate by semantic similarity?
    gmspflw = gmspflw[~gmspflw.duplicated(keep="first")]    # all fields
    gmspflw = gmspflw[~gmspflw["lemma"].duplicated(keep=False)] # lemma only

    # set lemma as index
    gmspflw = gmspflw.set_index("lemma")


    # 15. Save the final table as TSV.
    gmspflw.to_csv(
        os.path.join(outpath, "celex_nouns.tsv"),
        sep="\t",
        index=True,
        header=True
    )


if __name__ == "__main__":
    main()