# prerequisites: data_utils/prepare_celex_gecodb.py is run,
#                and prepared GeCoDB_v07 is available

import os

from germanet_search import is_germanet_noun
from load_datasets import load_gecodb


def main():

    # this file filters out all compounds not found in GermaNet;
    # the resulting dataset will be used to verify the lexical
    # constraints;
    # see previously done preprocessing of CELEX2:
    # https://github.com/maxschmaltz/DieKonstraints/blob/comp_constr_corp_study_mar26/data_utils/prepare_celex.py
    # see previously done preprocessing of GeCoDB_v05:
    # https://github.com/maxschmaltz/DieKonstraints/blob/comp_constr_corp_study_mar26/data_utils/prepare_gecodb.py

    datadir = "resources/developed"

    # We will proceed as follows:
    # 1. Init GeCoDB_v07.
    # 2. Filter out all GeCoDB_v07 entries not found
    # as nouns in Germanet (results in GeCoDB_v07_GN).
    # 3. Save the prepared data.

    # 1. Init GeCoDB_v07.

    # load prepared GeCoDB
    # (N=275409)
    gecodb_v07 = load_gecodb(os.path.join(datadir, "gecodb_v07.tsv"))


    # 2. Filter out all GeCoDB_v06 entries whose constituents
    # were not found as nouns in Germanet.

    gecodb_v07_gn = gecodb_v07[gecodb_v07["comp_lemma"].map(is_germanet_noun)]


    # 3. Save the prepared data.

    # (N=52433)
    gecodb_v07_gn.to_csv(
        os.path.join(datadir, "gecodb_v07_gn.tsv"),
        sep="\t",
        index=True,
        header=True
    )


if __name__ == "__main__":
    main()