# Prerequisites: prepare_celex.py has been run and prepared CELEX data is available.


import os
import math
# import asyncio
import pandas as pd
from tqdm import tqdm

from gecodb_compound_parser import Compound
from dereko_search import get_dereko_counts


def calculate_n1_prod(gecodb: pd.DataFrame) -> None:
    for lemma in tqdm(gecodb["n1_lemma"].unique(), desc="Calculating N1 prod"):
        # productivity: how many compounds there are with this N1
        n1_mask = gecodb["n1_lemma"] == lemma
        n1_prod = n1_mask.sum()
        gecodb.loc[n1_mask, "n1_prod"] = n1_prod
        # mass frequency: sum of frequencies of all compounds with this N1
        n1_mass_freq = gecodb.loc[n1_mask, "comp_freq"].sum()
        gecodb.loc[n1_mask, "n1_mass_freq"] = n1_mass_freq


def main():

    # In preparing GeCoDB, we need to to the following:
    # 1. Filter out all the compounds whose constituents 
    #   are not present in CELEX and those whose modifier frequency < 10
    # 2. Filter out compounds with deletion linkers
    # 3. Remove occasional duplicates
    # 4. Get counts for the compounds from DeReKo using the same procedure
    #   as for CELEX nouns (done in dereko_search.py) to remain consistent
    # 5. Recalculate productivities of N1s
    #   (since many compounds have been removed), keep
    #   compounds with modifier productivity >= 10
    # 6. Perform a few lesser transformations.
    # 7. Save the prepared GeCoDB to a new TSV file.

    gecodb_path = "resources/DeCOW16AX-comps/decow16ax_comps.tsv"
    celex_path = "resources/developed/celex_nouns.tsv"
    outpath = "resources/developed/gecodb_v06.tsv"

    # load prepared CELEX nouns
    celex = pd.read_csv(
        celex_path,
        sep="\t",
        dtype=str,
        header=0,
        index_col="lemma"
    )

    # load GeCoDB
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
        names=["comp_gecodb", "n1_prod"]
    )


    # 1. Remove all compounds whose constituents are not in CELEX

    # first, get N1 and N2 lemmas; since we will be needing both
    # N1, N2, and compound lemmas, we analyze compounds

    gecodb_v05["comp_lemma"], gecodb_v05["n1_lemma"], gecodb_v05["n2_lemma"] = zip(
        *gecodb_v05["comp_gecodb"].apply(
            lambda x: (
                (c := Compound(x)).lemma.capitalize(), c.stems[0].morph, c.stems[1].morph
            )
        )
    )

    # keep only those compounds whose N1 and N2 lemmas are in CELEX
    # and those whose modifiers build < 10 compounds
    gecodb_v05 = gecodb_v05[
        (gecodb_v05["n1_lemma"].isin(celex.index))
        & (gecodb_v05["n2_lemma"].isin(celex.index))
    ]

    # transfer N1, N2 frequencies from CELEX
    gecodb_v05["n1_freq"] = gecodb_v05["n1_lemma"].apply(
        lambda x: celex.loc[x, "freq"]
    )
    gecodb_v05["n2_freq"] = gecodb_v05["n2_lemma"].apply(
        lambda x: celex.loc[x, "freq"]
    )

    # then, remove N1s with productivity < 10
    gecodb_v05 = gecodb_v05[gecodb_v05["n1_prod"] >= 10]

    
    # 2. Remove compounds with deletion linkers

    gecodb_v05 = gecodb_v05[~gecodb_v05["comp_gecodb"].str.contains("-e")]


    # 3. Remove occasional duplicates
    gecodb_v05 = gecodb_v05[~gecodb_v05.duplicated(keep="first")]


    # 4. Get DeReKo counts for the compounds and drop
    # those below frequency threshold
    
    lemmas = gecodb_v05["comp_lemma"].tolist()

    # run in batches to enforce regular caching
    freqs = []
    batch_size = 2500
    progress_bar = tqdm(
        total=math.ceil(len(lemmas) / batch_size),
        desc="Retrieving KorAP frequencies in batches"
    )
    for batch_start in range(0, len(lemmas), batch_size):
        batch = lemmas[batch_start:batch_start + batch_size]
        # Note: after receiving a Meldung from IDS Mannheim support team,
        # we learned that our async requests were causing issues on their servers,
        # and so we provide a synchronous alternative below.
        # Previously:
        #   >>> batch_freqs = asyncio.run(aget_dereko_counts(batch))
        batch_freqs = get_dereko_counts(batch)
        freqs.extend(batch_freqs)
        progress_bar.update(1)
    gecodb_v05["comp_freq"] = freqs

    # freq check
    # lower freq for compounds as they are generally
    # more loose and free to produce
    freq_threshold = 20
    gecodb_v05 = gecodb_v05[gecodb_v05["comp_freq"] >= freq_threshold]


    # 5. Recalculate productivities of N1s
    # and remove compounds with N1 productivity < 10

    calculate_n1_prod(gecodb_v05)   # in place
    n1_prod_threshold = 10
    gecodb_v05 = gecodb_v05[gecodb_v05["n1_prod"] >= n1_prod_threshold]


    # 6. Lesser transformations

    # replace all _+er_ with _+=er_ (since the -(")er- linker always 
    # puts an umlaut on the stem if possible)
    gecodb_v05["comp_gecodb"] = gecodb_v05["comp_gecodb"].str.replace("_+er_", "_+=er_")

    # save freqs as integers
    gecodb_v05["comp_freq"] = gecodb_v05["comp_freq"].astype(int)
    gecodb_v05["n1_freq"] = gecodb_v05["n1_freq"].astype(int)
    gecodb_v05["n1_prod"] = gecodb_v05["n1_prod"].astype(int)
    gecodb_v05["n1_mass_freq"] = gecodb_v05["n1_mass_freq"].astype(int)
    gecodb_v05["n2_freq"] = gecodb_v05["n2_freq"].astype(int)

    # make reasonable ordering
    gecodb_v05 = gecodb_v05[
        [
            "comp_gecodb", "comp_lemma", "comp_freq",
            "n1_lemma", "n1_freq", "n1_prod", "n1_mass_freq",
            "n2_lemma", "n2_freq"
        ]
    ]

    # set compound as index
    gecodb_v05 = gecodb_v05.set_index("comp_gecodb")


    # 7. Save the prepared GeCoDB
    gecodb_v05.to_csv(
        outpath,
        sep="\t",
        index=True,
        header=True
    )


if __name__ == "__main__":
    main()