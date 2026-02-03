# Prerequisites: prepare_celex.py has been run and prepared CELEX data is available.


import os
import asyncio
import pandas as pd

from gecodb_compound_parser import Compound
from dereko_search import get_dereko_counts


def main():

    # In preparing GecoDB, we need to to the follwoing:
    # 1. Filter out all the compounds whose N1 are not present in CELEX
    #   and those with modifier frequency < 10
    # 2. Filter out compounds with deletion linkers
    # 3. Get counts for the compounds from DeReKo using the same procedure
    #    as for CELEX nouns (done in dereko_search.py) to remain consistent
    # 4. Recalculate productivities of N1s
    #   (since many compounds have been removed), keep
    #   compounds with modifier productivity >= 10
    # 5. Perform a few lesser transformations.
    # 6. Save the prepared GecoDB to a new TSV file.

    gecodb_path = "resources/GeCoDB/gecodb_v05.tsv"
    outpath = "resources/custom/compounding/intermediate_data"

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
        dtype={
            "comp": str,
            "n1_prod": int
        },
        header=None,
        # since freqs of the compounds
        # will be recomputed, no need to load them here
        usecols=[0, 2],
        names=["comp", "n1_prod"]
    )


    # 1. Remove all N1 that are not in CELEX and those
    # who build < 10 compounds

    # first, get N1 lemmas; since each linker starts with a "_"
    # and N1s in GeCoDB are always stored as lemmas
    # (no umlauting or deletion even if applicable),
    # we can simply split by "_" and take the first element,
    # no full analysis needed

    gecodb_v05["n1_lemma"] = gecodb_v05["comp"].apply(
        lambda x: x.split("_")[0]
    )

    gecodb_v05 = gecodb_v05[gecodb_v05["n1_lemma"].isin(celex.index)]

    # then, remove N1s with productivity < 10
    gecodb_v05 = gecodb_v05[gecodb_v05["n1_prod"] >= 10]

    # transfer n1 frequencies from celex
    gecodb_v05["n1_freq"] = gecodb_v05["n1_lemma"].apply(
        lambda x: celex.loc[x, "freq"]
    )

    
    # 2. Remove compounds with deletion linkers

    # remove all compounds with deletion linkers
    gecodb_v05 = gecodb_v05[~gecodb_v05["comp"].str.contains("-e")]


    # 3. Get DeReKo counts for the compounds and drop
    #   those below frequency threshold
    lemmas = [
        Compound(comp).lemma.capitalize()
        for comp in gecodb_v05["comp"].to_list()
    ]
    # run in batches to enforce regular caching
    freqs = []
    batch_size = 10000
    for batch_start in range(0, len(lemmas), batch_size):
        batch = lemmas[batch_start:batch_start + batch_size]
        batch_freqs = asyncio.run(get_dereko_counts(batch))
        freqs.extend(batch_freqs)
    gecodb_v05["comp_freq"] = freqs


    # 4. Recalculate productivities of N1s
    for lemma in gecodb_v05["n1_lemma"].unique():
        # productivity: how many compounds there are with this N1
        n1_mask = gecodb_v05["n1_lemma"] == lemma
        n1_prod = n1_mask.sum()
        gecodb_v05.loc[n1_mask, "n1_prod"] = n1_prod
        # mass frequency: sum of frequencies of all compounds with this N1
        n1_mass_freq = gecodb_v05.loc[n1_mask, "comp_freq"].sum()
        gecodb_v05.loc[n1_mask, "n1_mass_freq"] = n1_mass_freq


    # 5. Lesser transformations

    # replace all _+er_ with _+=er_ (since the -er- linker always 
    # puts an umlaut on the stem if possible)
    gecodb_v05["comp"] = gecodb_v05["comp"].str.replace("_+er_", "_+=er_")

    # save freqs as integers
    gecodb_v05["comp_freq"] = gecodb_v05["comp_freq"].astype(int)
    gecodb_v05["n1_freq"] = gecodb_v05["n1_freq"].astype(int)
    gecodb_v05["n1_prod"] = gecodb_v05["n1_prod"].astype(int)
    gecodb_v05["n1_mass_freq"] = gecodb_v05["n1_mass_freq"].astype(int)

    # make reasonable ordering
    gecodb_v05 = gecodb_v05[
        ["comp", "comp_freq", "n1_lemma", "n1_freq", "n1_prod", "n1_mass_freq"]
    ]

    # set compound as index
    gecodb_v05 = gecodb_v05.set_index("comp")


    # 6. Save the prepared GecoDB
    gecodb_v05.to_csv(
        os.path.join(outpath, "gecodb_v06.tsv"),
        sep="\t",
        index=True,
        header=True
    )


if __name__ == "__main__":
    main()