import os
import pandas as pd
from collections import defaultdict
from typing import Tuple

from dereko_search import get_dereko_matches


def main():

    # TODO: COMMENT

    datadir = "resources/developed"

    # We will proceed as follows:
    # ...
    
    # load prepared GeCoDB
    # (N=2100)
    gecodb_v07pl = pd.read_csv(
        os.path.join(datadir, "gecodb_v07pl_300er_sample.tsv"),
        sep="\t",
        header=0,
        index_col=0
    )

    matches = get_dereko_matches(gecodb_v07pl["comp_lemma"].values.tolist())



    


if __name__ == "__main__":
    main()