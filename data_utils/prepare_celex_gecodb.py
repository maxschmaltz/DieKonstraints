import os
import pandas as pd
from collections import defaultdict
from typing import Tuple

from gecodb_compound_parser import Compound
from germanet_search import is_germanet_noun


def main():

    # this file filters out all N1 not found in
    # GermaNet, and compounds built with this N1;
    # see previously done preprocessing of CELEX2:
    # https://github.com/maxschmaltz/DieKonstraints/blob/comp_constr_corp_study_mar26/data_utils/prepare_celex.py
    # see previously done preprocessing of GeCoDB_v05:
    # https://github.com/maxschmaltz/DieKonstraints/blob/comp_constr_corp_study_mar26/data_utils/prepare_gecodb.py

    celex_path = "resources/comp_constr_corp_study_mar26/celex_nouns.tsv"
    gecodb_path = "resources/comp_constr_corp_study_mar26/gecodb_v06.tsv"
    outdir = "resources/developed"
    os.makedirs(outdir, exist_ok=True)

    # We will proceed as follows:
    # 1. Init CELEX-nouns, GeCoDB_v06.
    # 2. Filter out all CELEX-nouns entries not found as nouns in Germanet.
    # 3. Filter out all GeCoDB_v06 entries whose constituents 
    # were not found as nouns in Germanet (results in GeCoDB_v07).
    # 4. Explicitly extract linker from GeCoDB_v07 entries.
    # 5. Minor modifications of GeCoDB_v07.
    # 6. Save the prepared data to new TSV files.

    # 1. Init CELEX-nouns, GeCoDB_v06.
    
    # load prepared CELEX nouns
    # (N=11996)
    celex = pd.read_csv(
        celex_path,
        sep="\t",
        dtype=str,
        header=0,
        index_col="lemma"
    )

    # load prepared GeCoDB
    # (N=282767)
    gecodb_v06 = pd.read_csv(
        gecodb_path,
        sep="\t",
        dtype=defaultdict(
            lambda: str,
            **{
                f"{prx}_freq": int
                for prx in ["comp", "n1", "n1_mass", "n2"]
            },
            n1_prod="int"
        ),
        header=0,
        index_col=0
    )


    # 2. Filter out all CELEX-nouns entries not found as nouns in Germanet.

    celex["is_germanet_noun"] = celex.index.map(is_germanet_noun)
    # extract negatives for faster filtering of GeCoDB
    celex_stop = celex[~celex["is_germanet_noun"]]
    celex = celex[celex["is_germanet_noun"]]
    celex.drop(columns=["is_germanet_noun"], inplace=True)


    # 3. Filter out all GeCoDB_v06 entries whose constituents
    # were not found as nouns in Germanet.

    gecodb_v07 = gecodb_v06[
        ~(gecodb_v06["n1_lemma"].isin(celex_stop.index)) &
        ~(gecodb_v06["n2_lemma"].isin(celex_stop.index))
    ]


    # 4. Explicitly extract linker from GeCoDB_v06 entries.

    def extract_linker(gecodb: str) -> Tuple[str, bool]:
        comp = Compound(gecodb)
        linker = comp.linkers[0]
        umlaut_applied = (
            linker.adds_umlaut and
            not comp.lemma.startswith(comp.stems[0].morph)
        )
        return linker.gecodb, umlaut_applied
    
    gecodb_v07["linker"], gecodb_v07["umlaut_applied"] = zip(
        *gecodb_v07.apply(
            lambda row: extract_linker(row.name),
            axis=1
        )
    )

    # to investigate the effect of the umlaut on
    # plural effect, we disambugate between -"er- and -er-
    er_numl = gecodb_v07[
        (gecodb_v07["linker"] == "_+=er_") &
        ~(gecodb_v07["umlaut_applied"])
    ]
    gecodb_v07.loc[er_numl.index, "linker"] = "_+er_"

    # identify whether the linker is pluralic
    def is_pll(gecodb: str) -> bool:
        comp = Compound(gecodb)
        linker = comp.linkers[0]
        # exclude 0 and -s-
        if not linker.gecodb in [
            "_+n_", "_+en_",
            "_+e_", "_+=e_",
            "_+=_",
            "_+er_", "_+=er_"
        ]:
            return False
        # because of cases like 'Sternenwiese'
        # or 'Mausefalle', we cannot simply check
        # if the linker is in the list of all pluralic linkers,
        # so we retrieve the Pl form of N1 instead
        n1 = comp.stems[0]
        expected_pl = celex.loc[n1.morph]["nom_pl"]
        if pd.isna(expected_pl):
            # no Pl form
            return False
        expected_pls = expected_pl.split("/")
        # linker + maybe umlaut
        maybe_pl = n1.allomorph + linker.allomorph
        # account for several Pl form variants
        return any(maybe_pl in expected_pl for expected_pl in expected_pls)
    
    gecodb_v07["is_pll"] = gecodb_v07.index.map(is_pll)


    # 5. Minor modifications of GeCoDB_v07.

    # remove possible toponyms (N=4227)
    toponym_n2s = [
        "straße", "gasse", "weg", "allee", "platz",
        "dorf", "burg", "berg", "hof", "eck", "stein"
    ]
    gecodb_v07 = gecodb_v07[~gecodb_v07["n2_lemma"].isin(toponym_n2s)]

    # remove duplicates (N=1)
    gecodb_v07 = gecodb_v07[~gecodb_v07.index.duplicated(keep="first")]

    # sort columns
    gecodb_v07 = gecodb_v07[[
        "comp_lemma", "comp_freq",
        "n1_lemma", "n1_freq", "n1_prod", # "n1_mass_freq",
        "linker", "is_pll", "umlaut_applied",
        "n2_lemma", "n2_freq"
    ]]


    # 6. Save the prepared data to new TSV files.
    
    # (N=10999, deleted N=997)
    celex.to_csv(
        os.path.join(outdir, "celex_nouns.tsv"),
        sep="\t",
        index=True,
        header=True
    )

    # (N=277361, deleted N=5406 (not in GermaNet N=1178, duplicate N=1, toponyms N=4227))
    gecodb_v07.to_csv(
        os.path.join(outdir, "gecodb_v07.tsv"),
        sep="\t",
        index=True,
        header=True
    )


if __name__ == "__main__":
    main()