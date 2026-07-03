import os
import pandas as pd
from collections import defaultdict

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
    # 1. Init CELEX-nouns, GeCoDB_v06
    # 2. Filter out all CELEX-nouns entries not found as nouns in Germanet
    # 3. Filter out all GeCoDB_v06 entries whose constituents were not found as nouns in Germanet
    # 4. Save the prepared data to new TSV files.

    # 1. Init CELEX-nouns, GeCoDB_v06
    
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
            }
        ),
        header=0,
        index_col=0
    )


    # 2. Filter out all CELEX-nouns entries not found as nouns in Germanet

    celex["is_germanet_noun"] = celex.index.map(is_germanet_noun)
    # extract negatives for faster filtering of GeCoDB
    celex_stop = celex[~celex["is_germanet_noun"]]
    celex = celex[celex["is_germanet_noun"]]
    celex.drop(columns=["is_germanet_noun"], inplace=True)


    # 3. Filter out all GeCoDB_v06 entries whose constituents were not found as nouns in Germanet

    gecodb_v07 = gecodb_v06[
        ~(gecodb_v06["n1_lemma"].isin(celex_stop.index)) &
        ~(gecodb_v06["n2_lemma"].isin(celex_stop.index))
    ]


    # 4. Save the prepared data to new TSV files.
    
    # (N=10999, deleted N=997)
    celex.to_csv(
        os.path.join(outdir, "celex_nouns.tsv"),
        sep="\t",
        index=True,
        header=True
    )

    # (N=281589, deleted N=1178)
    gecodb_v07.to_csv(
        os.path.join(outdir, "gecodb_v07.tsv"),
        sep="\t",
        index=True,
        header=True
    )


if __name__ == "__main__":
    main()