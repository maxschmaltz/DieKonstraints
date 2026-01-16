# Prerequisites: prepare_celex.py has been run and prepared CELEX data is available.
#                prepare_gecodb.py has been run and prepared GeCoDB data is available.


import os
import pandas as pd
import yaml


def main():
    
    # outpath = "resources/custom/compounding/intermediate_data"

    # # load prepared CELEX nouns
    # celex = pd.read_csv(
    #     os.path.join(outpath, "celex_nouns.tsv"),
    #     sep="\t",
    #     dtype=str,
    #     header=0,
    #     index_col="lemma"
    # )

    # # load GecoDB
    # gecodb_v05 = pd.read_csv(
    #     os.path.join(outpath, "gecodb_v06.tsv"),
    #     sep="\t",
    #     dtype=str,
    #     header=None,
    #     names=["comp", "comp_freq", "n1_freq"]
    # )

    # load constraints
    with open("compounding/constraints/constraints.yaml", encoding="utf-8") as f:
        constraints = list(yaml.safe_load_all(f))[-1]["constraints"]

    pass


    # For checking the applicability and application of constraints,
    # we follow the algorithm:
    # 1. For each lemma in CELEX, check and record applicability
    #   of each constraint.
    # 2. For each compound in GeCoDB, run corresponding application checks
    #   for each constraint that was applicable to its N1. Record results.
    # 3. Calculate statistics.
    # 4. Save results.



if __name__ == "__main__":
    main()
