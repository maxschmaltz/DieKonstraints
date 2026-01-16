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
    # 2. Filter `gml.cd` for non-derivative nouns.
    # 3. Parse `gsl.cd`.
    # 4. Join `gml.cd` and `gsl.cd` on lemma id.
    # 5. Parse `gmw.cd`.
    # 6. Filter `gmw.cd` for GenSg and NomPl forms of the nouns
    #   in the filtered joint table from step 4.
    # 7. Join the filtered `gmw.cd` table to the filtered
    #   joint table from step 4 on lemma id.
    # 8. Parse `gpl.cd`.
    # 9. Filter `gpl.cd` for phonological and syllabic information
    #   of the nouns in the table from step 7. Convert phonological
    #   and notations into SAMPA.
    # 10. Join the filtered `gpl.cd` table to the table from step 7 on lemma id.
    # 11. Parse `gfl.cd`.
    # 12. Filter `gfl.cd` for frequency information of the nouns
    #   in the table from step 10.
    # 13. Join the filtered `gfl.cd` table to the table from step 10 on lemma id.
    # 14. Filter out lemmas with frequency below a certain threshold.
    #   Conduct orthographic transformations (umlauts, lowering).
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
    def parse_morphemic_structure_schema(drv_steps: str) -> tuple:

        morphemic_structure = []
        morphemic_schema = ""

        # Derivational history is recursively built as H = (H1, H2, ...)[POS],
        # where each Hi is also of form H1 = (H11, H21, ...)[POS].
        # However, since we are not interested (for now) in specific derivational steps
        # and their hierarchy, we only need to extract the high-level POS
        # and all low-level <morpheme-type> information.
        pos = re.search(r"\[(?P<pos>[A-Z|.]+)\]$", drv_steps).group("pos")
        for match in re.finditer(r"\((?P<m>[^()]+)\)\[(?P<t>[A-Z|.]+)\]", drv_steps):
            morpheme = match.group("m")
            m_type = match.group("t")
            m_type = "x" if "|" in m_type else m_type  # affixes ("x") are marked as "Xout|.Xin"
            morphemic_structure.append(morpheme)
            morphemic_schema += m_type

        return "-".join(morphemic_structure), morphemic_schema, pos
    
    gml["morphemic_structure"], gml["morphemic_schema"], gml["pos"] = zip(
            *gml["drvt_history"].apply(
                lambda x: parse_morphemic_structure_schema(x)
        )
    )

    # we can now drop the original `drvt_history` column
    gml = gml.drop(columns=["drvt_history"])


    # 2. Filter `gml.cd` for non-derivative nouns.

    # drop non-noun records
    gml = gml[gml["pos"] == "N"]
    # now we can drop the 'pos' column since we now have nouns only
    gml = gml.drop(columns=["pos"])

    # next, filter out all records that have more than
    # one stem in their morphemic schema; allow only
    # A(dj), V(erb), N(oun) stems and affixes (x);
    # additionally, allow lexicalized F(lexion) which
    # are in fact deverbatives (Essen, Abfahrt, etc.)
    # and deadjectives (Arme etc.)
    gml = gml[
        gml["morphemic_schema"].apply(
            lambda x: re.match(r"^x*[AVNF]x*$", x, flags=re.IGNORECASE) is not None
        )
    ]

    # filter out one- and two-character lemmas except for
    # 'Ei', 'Öl', 'As' (they are otherwise letter names or interjections)
    gml = gml[((gml["lemma"].str.len() > 2) | (gml["lemma"].isin(["Ei", "Öl", "As"])))]


    # 3. Next, we parse `gsl.cd`. For reference, see the CELEX documentation
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

    # drop records with any missing fields
    gsl = gsl.dropna()


    # 4. We join `gml.cd` and `gsl.cd` on lemma id.
    gmsl = gml.join(gsl, how="inner")

    # remove records with fluctuating gender
    # (it has more than one gender code in the 'gender' column,
    # see CELEX documentation 5-88)
    gmsl = gmsl[
        gmsl["gender"].apply(
            lambda x: len(x)
        ) == 1
    ]

    # we can also convert the gender codes to more readable values
    # (see CELEX documentation 5-88)
    gmsl["gender"] = gmsl["gender"].map({"1": "m", "2": "f", "3": "n"})


    # 5. Next, we parse `gmw.cd`. For reference, see the CELEX documentation
    # (5-83) and `gmw/README`.

    # The following columns are relevant:
    # * Column 2: Wordform.
    # * Column 4: Lemma id.
    # * Column 5: Paradigm codes (to identify GenSg and NomPl forms).

    gmw = pd.read_csv(
        os.path.join(celex_path, "gmw/gmw.cd"),
        sep="\\",
        header=None,
        dtype=str,
        usecols=[1, 3, 4],
        names=["wordform", "id", "paradigm_code"],
        index_col="id"
    )

    # drop records with any missing fields
    gmw = gmw.dropna()


    # 6. We filter `gmw.cd` for GenSg and NomPl forms of the nouns
    # in the filtered joint table from step 4.

    # remove wordforms of lemmas that are not in `gmsl`
    gmw = gmw[gmw.index.isin(gmsl.index.values)]

    # split records by `paradigm_code`; rewrites as one wordform per row, even if
    # multiple paradigm codes are assigned to the same wordform (e.g. Tiefe\nS,gS,dS,aS
    # will be rewritten as 4 rows: Tiefe\nS, Tiefe\gS, Tiefe\dS, Tiefe\aS)
    gmw = gmw.assign(paradigm_code=gmw["paradigm_code"].str.split(",")) # rewrites as list
    gmw = gmw.explode("paradigm_code")  # unscrambles into one entry per list item

    # keep only GenSg and NomPl forms
    gmw = gmw[gmw["paradigm_code"].isin(["gS", "nP"])]

    # pivot the table to have separate columns for GenSg and NomPl forms
    gmw = gmw.pivot_table(
        index=gmw.index,
        columns="paradigm_code",
        values="wordform",
        aggfunc="first"
    ).rename(columns={"gS": "gen_sg", "nP": "nom_pl"})


    # 7. We join the filtered `gmw.cd` table to the filtered
    # joint table from step 4 on lemma id. For that, we need to
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

    # convert CELEX DISC notation into SAMPA (X-SAMPA used)
    gpl = gpl["phonetic_transcription"].apply(
        lambda x: phonecodes.convert(
            # phonecodes cannot convert directly from disc to xsampa,
            # so we convert via ipa
            phonecodes.convert(
                x,
                "disc",
                "ipa",
                language="deu"
            ),
            "ipa",
            "xsampa",
            # for 'xsampa',
            # specifying a language is optional and ignored by the code,
            # since X-SAMPA is language agnostic
        # replace double quotes with asterisk for stress marker
        # for better TSV readability
        ).replace('"', "*")
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


    # 14. Filter out lemmas with frequency below a certain threshold.
    # Conduct orthographic transformations.

    # freq check
    freq_threshold = 5
    gmspflw = gmspflw[gmspflw["freq"].astype(int) >= freq_threshold]

    # lower and apply orthographic transformations of umlauts;
    # return Nonefor missing Pl forms
    umlambda = lambda x: \
        None if pd.isna(x) else \
        x.replace("ae", "ä").   \
        replace("oe", "ö").     \
        replace("ue", "ü").     \
        lower()
    
    target_columns = ["lemma", "morphemic_structure", "gen_sg", "nom_pl"]
    gmspflw[target_columns] = gmspflw[target_columns].apply(
        lambda col: col.apply(umlambda)
    )

    # final check: drop records with any missing fields except for `nom_pl`
    gmspflw = gmspflw.dropna(subset=list(set(gmspflw.columns) - {"nom_pl"}))

    # set lemma as index
    gmspflw = gmspflw.set_index("lemma")

    # remove doplicates
    gmspflw = gmspflw[~gmspflw.index.duplicated(keep="first")]


    # 15. Save the final table as TSV.
    gmspflw.to_csv(
        os.path.join(outpath, "celex_nouns.tsv"),
        sep="\t",
        index=True,
        header=True
    )


if __name__ == "__main__":
    main()