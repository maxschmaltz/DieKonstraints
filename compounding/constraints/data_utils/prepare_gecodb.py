# Prerequisites: prepare_celex.py has been run and prepared CELEX data is available.


import os
import pandas as pd


def main():

    # In preparing GecoDB, we need to 1) filter out all the compounds whos
    # N1 are not present in CELEX and 2) perform a few lesser transformations.

    gecodb_path = "resources/GeCoDB/gecodb_v05.tsv"
    outpath = "resources/custom/compounding/intermediate_data"
    os.makedirs(outpath, exist_ok=True)

    # load prepared CELEX nouns
    celex = pd.read_csv(
        os.path.join(outpath, "celex_nouns.tsv"),
        sep="\t",
        dtype=str,
        header=0,
        index_col="lemma"
    )

    # load GecoDB
    gecodb_v05 = pd.read_csv(
        gecodb_path,
        sep="\t",
        dtype=str,
        header=None,
        names=["comp", "comp_freq", "n1_freq"]
    )


    # 1. Remove all N1 that are not in CELEX

    # first, get N1 lemmas; since each linker starts with a "_"
    # and N1s in GeCoDB are always stored as lemmas
    # (no umlauting or deletion even if applicable),
    # we can simply split by "_" and take the first element,
    # no full analysis needed

    gecodb_v05["n1_lemma"] = gecodb_v05["comp"].apply(
        lambda x: x.split("_")[0]
    )

    gecodb_v05 = gecodb_v05[gecodb_v05["n1_lemma"].isin(celex.index)]

    
    # 2. Lesser transformations

    # remove all compounds with deletion linkers
    gecodb_v05 = gecodb_v05[~gecodb_v05["comp"].str.contains("-e")]

    # replace all _+er_ with _+=er_ (since the -er- linker always 
    # puts an umlaut on the stem if possible)
    gecodb_v05["comp"] = gecodb_v05["comp"].str.replace("_+er_", "_+=er_")

    # swap `n1_freq` and `n1_lemma` for more reasonable ordering
    gecodb_v05 = gecodb_v05[
        ["comp", "comp_freq", "n1_lemma", "n1_freq"]
    ]


    # 3. Save the prepared GecoDB
    gecodb_v05.to_csv(
        os.path.join(outpath, "gecodb_v06.tsv"),
        sep="\t",
        index=False,
        header=True
    )


if __name__ == "__main__":
    main()