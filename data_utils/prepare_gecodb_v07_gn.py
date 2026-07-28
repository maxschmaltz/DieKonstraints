# prerequisites: data_utils/prepare_celex_gecodb.py is run,
#                and prepared GeCoDB_v07 is available

import os

from germanet_search import get_n1_lexunit
from load_datasets import load_gecodb


def main():

    # this script filters out all compounds not found in GermaNet,
    # not recognized as compounds in GermaNet,
    # or those that cannot be parsed confidently in GermaNet;
    # the resulting dataset will be used to verify the lexical
    # and a few semantic constraints;
    # see previously done preprocessing of CELEX2:
    # https://github.com/maxschmaltz/DieKonstraints/blob/comp_constr_corp_study_mar26/data_utils/prepare_celex.py
    # see previously done preprocessing of GeCoDB_v05:
    # https://github.com/maxschmaltz/DieKonstraints/blob/comp_constr_corp_study_mar26/data_utils/prepare_gecodb.py

    datadir = "resources/developed"

    # We will proceed as follows:
    # 1. Init GeCoDB_v07.
    # 2. Filter out all GeCoDB_v07 entries that cannot be parsed
    # confidently in GermaNet (results in GeCoDB_v07_GN).
    # 3. Save the prepared data.

    # 1. Init GeCoDB_v07.

    # load prepared GeCoDB
    # (N=275411)
    gecodb_v07 = load_gecodb(os.path.join(datadir, "gecodb_v07.tsv"))


    # 2. Filter out all GeCoDB_v07 entries that cannot be parsed
    # confidently in GermaNet.

    # Since the target constraints require an unambiguous specification
    # of certain meanings (animal, person, mass), we need to be able
    # to unambiguously retrieve specific N1 and its properties,
    # which becomes vital with polysemous N1s: 'Glasfenster' vs 'Gläserregal'.
    # We will therefore filter out all compounds that have more
    # than one entries in GermaNet or whose N1s are specified as several possibilities.

    gecodb_v07_gn = gecodb_v07[
        gecodb_v07["comp_lemma"].map(
            # returns None if the compound is not found
            # or not recognized as a compound in GeraNet,
            # or if several compound or N1 analyses are indicated
            lambda x: get_n1_lexunit(x) is not None
        )
    ]


    # 3. Save the prepared data.

    # (N=48980)
    gecodb_v07_gn.to_csv(
        os.path.join(datadir, "gecodb_v07_gn.tsv"),
        sep="\t",
        index=True,
        header=True
    )


if __name__ == "__main__":
    main()