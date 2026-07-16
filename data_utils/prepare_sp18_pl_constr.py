# prerequisites: 'data_utils/prepare_sp18.py' has been run, 
# and the output of that script is available in 'resources/developed/sp18'.

import os
import pandas as pd
from collections import defaultdict


def main():

    # This script prepares the default version of SP18 dataset
    # with lemmatized compounds for measuring the pluralic constraints.
    # 
    # (UniqN=x) refers to the number of unique compound **lemmata** in the dataset,
    # (UniqN1N=x) refers to the number of N1 **lemmata** in the dataset.
    # 'Compounds' refers to 'compound lemmata' unless specified otherwise.
    #
    # The default SP18 contains N=8212, UniqN=6889 lemmatized compounds
    # in Sg and Pl forms (different cases) with individual or collective meaning of N1.
    # The columns are as follows:
    #   gecodb: the GeCoDB notation of compound lemma.
    #   n1: N1 in the lemmatized form.
    #   n2: N2 in the lemmatized form.
    #   n1_pl_marker: the plural type (marker) of N1 converted to
    #       the GeCoDB notation.
    #   n1_sem: the meaning of N1 (as forced by N2).
    #       Either "ind" (individual), or "coll" (collective), or "konvc" (ambiguous).
    #   n2_num: grammatical number of N2 (hence, the entire compound).
    #       Either "Sg" or "Pl", case not indicated.
    #   is_linker_pl: whether the linking element is pluralic or not.
    #       Either 1 or 0, respectively.
    #   wc: WC of lemma in DeReKo.
    #   context: context sentence.
    #   context_id: the unique id of the context sentence. This is the column
    #       by which this metadata can be joined back to the dataset.

    # The dataset resulting from this script will be used for
    # measuring the coverage and the regularity of the pluralic constraints.
    # We will be reproducing the same workflow as in Shmalts 2026,
    # and will be looking at the constraints at the lexical
    # level. That means that for this dataset, we will be counting lemmata and not
    # tokens, we won't be needing the N1s to appear both with a Sg and a Pl meaning,
    # and we won't investigate any frequency or problematic group effects. However, note
    # that in case of a doubtful case (e.g. 'Apfelbaum' vs 'Äpfelbaum'), both
    # variants will be kept as long as they pass the frequency threshold.
    #
    # Thus, the main goals of this script is to create a
    # deduplicated version of SP18 for verification of the pluralic constraints.

    # The overall IntPE dataset preprocessing includes the following:
    #   1. Load SP18.
    #   2. Apply frequency filter.
    #   3. Deduplicate the sample (keep doubtful cases).
    #   4. Remove unnecessary columns (e.g. context, context_id, etc.).
    #   5. Save the resulting dataset.


    sp18_dir = "resources/developed/sp18"


    # 1. Load SP18.
    
    # SP18 (N=8212, UniqN=6889, UniqN1N=46)
    sp18 = pd.read_csv(
        os.path.join(sp18_dir, "sp18.tsv"),
        sep="\t",
        header=0,
        index_col="gecodb",
        # all str, WC int, is linker pluralic bool
        dtype=defaultdict(
            lambda: str,
            wc="int",
            is_linker_pl="bool"
        ),
        quoting=3   # = csv.QUOTE_NONE, separate by tabs only
    )


    # 2. Apply frequency filter.

    # (N=3626, UniqN=2681, UniqN1N=44)
    sp18 = sp18[sp18["wc"] >= 20]


    # 3. Deduplicate the sample (keep doubtful cases).

    # (UniqN=2681, UniqN1N=44)
    sp18_pl_constr = sp18[~sp18.index.duplicated(keep="first")]

    
    # 4. Remove unnecessary columns (e.g. context, context_id, etc.).
    sp18_pl_constr.drop(
        columns=["n2_num", "context", "context_id"],
        inplace=True
    )


    # 5. Save the resulting dataset.
    sp18_pl_constr.to_csv(
        os.path.join(sp18_dir, "sp18_pl_constr.tsv"),
        sep="\t",
        index=True,
        header=True
    )


if __name__ == "__main__":
    main()