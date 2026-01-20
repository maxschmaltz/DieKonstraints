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
    #   and notations into SAMPA.
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


    # 3. Filter `gml.cd` for non-c nouns.

    # first, filter out all records that have more than
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

    # now, lexicalized F(lexion) stems are stored in CELEX
    # with no analysis: they are underspecified by their
    # derivational history (deverbal or deadjectival) and
    # morphemic structure (e.g. no prefixes are indicated);
    # because of that, we need to unparse them separately
    # based on their respective lemmas
    def _unparse_verb(row: pd.Series) -> tuple[str, str]:
        # deverbative, return verb's morphemic structure/schema
        # plus -en/-n suffix since CELEX does not include it
        if row["lemma"] in ["sein", "tun"]: # irregular
            marker = "-n"
        else:
            marker = re.search(r"(e?n)$", row["lemma"]).group(1)
        return (
            row["morphemic_structure"] + f"-{marker}",
            row["morphemic_schema"] + "x"
        )
    
    def _unparse_adjective(row: pd.Series) -> tuple[str, str]:
        pass

    def _unparse_unspecified(gml_id: int) -> tuple[str, str]:
        try:
            orig_info = gml.loc[gml_id]
            if orig_info["pos"] == "V":
                return _unparse_verb(orig_info)
            else:   # elif orig_info["pos"] == "A":
                return _unparse_adjective(orig_info)
        except KeyError:
            return None, None

    def _unparse_lexicalized_flexion(
        row: pd.Series,
        gml: pd.DataFrame,
        gmw: pd.DataFrame
    ) -> tuple[str, str]:
        # filter for nouns later, as of now we need V and A for unparsing
        if row["pos"] != "N" or "F" not in row["morphemic_schema"]:
            return row["morphemic_structure"], row["morphemic_schema"]
        # first, identify the F itself
        lex_f = row["morphemic_structure"].split("-")[row["morphemic_schema"].index("F")]
        # now look up and analyze
        lex_f_entries = gml[gml["lemma"] == lex_f]
        if not len(lex_f_entries):
            pass
        if len(lex_f_entries) == 1:
            lex_f_info = lex_f_entries.iloc[0]
            if lex_f_info["pos"] == "V":
                return _unparse_verb(lex_f_info)
            elif lex_f_info["pos"] == "A":
                # there are two variants for Adj lexicalized (F)lexion stems in CELEX:
                # Partizipien (as 'angelegen' in 'Angelegenheit')
                # or adjective forms (as 'besser' in 'Besserung');
                # both variants can be found in `gmw.cd` as separate wordforms:
                # `pA` is the code for Partizipien, `c0` is the code for adjective forms;
                # from where we will be able to extract the original verbal/adjective stem
                lex_f_forms = gmw[
                    (gmw["wordform"] == lex_f)
                    & gmw["paradigm_code"].apply(
                        lambda x: ("pA" in x) or ("c0" in x)
                    )
                ]
                if (not len(lex_f_forms)) or len(lex_f_forms) > 1:
                    # underanalysis or ambiguity, both unreliable
                    # (latter; only a few cases found,
                    # e.g. 'abgewogen' for 'abwägen' and 'abwiegen'
                    # and 'bedacht' for 'bedenken' and 'bedachen')
                    # TODO: resolve by semantic semelarity?
                    if len(gml.loc[lex_f_forms.index.values]["pos"].isin(["V", "A"])) != 1:
                        return None, None
                    else:
                        orig_id = lex_f_forms[
                            gml.loc[lex_f_forms.index.values]["pos"].isin(["V", "A"])
                        ].index[0].item()
                        return _unparse_unspecified(orig_id)
                else:
                    orig_id = lex_f_forms.index[0].item()
                    return _unparse_unspecified(orig_id)
            else:   # elif lex_f_info["pos"] == "N":
                # there are two variants for Noun lexicalized (F)lexion stems in CELEX:
                # adjectives in weak deadjectival nouns (as 'arm' in 'Arme')
                # or lexicalized deverbals such (as 'Fahrt' in 'Abfahrt')
                pass
                
        else:
            pass

    gml[["morphemic_structure", "morphemic_schema"]] = gml.apply(
        # pass gml and gmw for lookups
        lambda row: _unparse_lexicalized_flexion(row, gml, gmw),
        axis=1
    )

    # drop records with any missing fields repeatedly
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

    # drop records with any missing fields
    gsl = gsl.dropna()


    # 5. We join `gml.cd` and `gsl.cd` on lemma id.
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
    gml = gml[((gml["lemma"].str.len() > 2) | (gml["lemma"].isin(["Ei", "Öl", "As"])))]

    # final check: drop records with any missing fields except for `nom_pl`
    gmspflw = gmspflw.dropna(subset=list(set(gmspflw.columns) - {"nom_pl"}))

    # set lemma as index
    gmspflw = gmspflw.set_index("lemma")

    # remove duplicates
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