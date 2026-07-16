# prerequisites: 'data_utils/prepare_sp18.py' has been run, 
# and the output of that script is available in 'resources/developed/sp18'.

import os
import yaml
import pandas as pd
from collections import defaultdict
from tqdm import tqdm
from typing import Tuple

from check_applicability import applicability_checkers
from .gecodb_compound_parser import Compound


# python3 -m data_utils.prepare_sp18_intpe
def main():

    # This script prepares the default version of SP18 dataset
    # with lemmatized compounds for investigation of the
    # internal plural effect (IntPE).
    #
    # Convention: (N=x) refers to the number of compound **tokens** in the dataset, 
    # (UniqN=x) refers to the number of unique compound **lemmata** in the dataset,
    # (UniqN1N=x) refers to the number of N1 **lemmata** in the dataset.
    # 'Compounds' refers to 'compound tokens' unless specified otherwise.
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

    # The dataset resulting from this script will be used for investigation
    # of the IntPE as a followup to Schäfer & Pankratz 2018.
    # While Schäfer & Pankratz 2018 find evidence for the IntPE,
    # the followup investigation of ExtPE revealed a small frequency
    # effect and an episodic "group contamination" effect. We will therefore
    # reproduce the IntPE experiment with the same "decontamination"
    # and frequency filtering method. Since the ExtPE was not confirmed
    # and cannot build its own problematic group, there are only
    # two:
    # 1. Compounds whose N1 only appear with a Sg or only with a Pl meaning.
    # Since the IntPE is triggered by semantical plurality of the N1,
    # this N1 should occur both with a Sg and with a Pl meaning in order to
    # validate whether the IntPE takes place. Otherwise, it is impossible
    # to make judgments about the expected behavior of these compounds
    # with the opposite meaning.
    # 2. Compounds whose N1s are forced to attach the pluralic linker 
    # due to other constraints, e.g. because of schwa ('Katzenfell' vs. 'Katzenfelle',
    # found in the data) or as a person designation ('Kinderbuch' vs. 'Kinderbücher',
    # found in the data). If the given N1 mostly takes a pluralic linker,
    # it will most likely do with a Pl meaning of N1, making the IntPE undetectable.
    #
    # Similar to ExtPE, our idea for investigating the IntPE is to confront
    # contrastive pairs of compounds built from the same N1s with a Sg and a Pl meaning
    # (e.g. 'Buch' + 'Deckel' is 'Buchdeckel' with a Sg meaning, will
    # 'Buch' + 'Regal' become 'Bücherregal' due to a Pl meaning?).
    # Thus, the main goals of this script is to
    # Detect and filter out the two problematic groups and 
    # extract the contrastive groups of compounds with Sg-Pl meaning of N1,
    # while saving the intermediate data collections in order to enable
    # ablation studies on how strongly each of this group interfere with the IntPE.

    # The overall preprocessing includes the following:
    #   1. Load SP18.
    #   2. Load the constraints.
    #   3. Leave out compounds whose N1s do not exhibit an alternation between
    #   Sg vs. Pl meaning.
    #   4. Leave out compounds whose N1 may attach the pluralic linker
    #   due to other constraints.
    # Note that the original dataset was constructed by sampling up to
    # 100 compounds per N1, so no additional step to filter out
    # compounds with unique N1s is needed (which has also been verified
    # separately).


    # As a result of the preprocessing, we obtain the following datasets
    # (all have the same notation as SP18):
    #
    #   * 'resources/developed/sp18/intpe/alt.tsv'
    #   (N=2318, UniqN=1246, UniqCN=869)
    #   Compounds built from N1s appearing both with a Sg and with a Pl meaning
    #
    #   * 'resources/developed/sp18/intpe/leftovers/nalt_sg.tsv'
    #   (N=892)
    #   Compounds built from N1s appearing only with a Sg meaning
    #
    #   (N=0)
    #   (Compounds built from N1s appearing only with a Pl meaning)
    #
    #
    #   * 'resources/developed/sp18/intpe/alt_npll.tsv'
    #   (N=1236, UniqN=665, UniqCN=468, UniqN1N=30)
    #   Compounds built from N1s appearing both with a Sg and with a Pl meaning
    #   that may not attach a pluralic linker
    #
    #   * 'resources/developed/sp18/intpe/leftovers/alt_pll.tsv'
    #   (N=695, UniqN1N=16)
    #   Compounds built from N1s appearing both with a Sg and with a Pl meaning
    #   that may attach a pluralic linker
    #
    #
    #
    #   * 'resources/developed/sp18/intpe/summaries/n1_sem.tsv'
    #   (UniqCN=869)
    #   Counts of compounds with 'ind'/'coll'/'konvc' N1 meaning 
    #   built from each N1 (from 'resources/developed/sp18/sp18.tsv')
    #
    #   * 'resources/developed/sp18/intpe/summaries/alt_constr.tsv'
    #   (UniqN1N=46)
    #   Record of applicable N1-targeting constraints for each unique N1
    #   (from 'resources/developed/sp18/intpe/alt.tsv')

    # Thus, the data tree looks as follows:
    #
    #          SP18
    #   lemmatized compounds
    #  (N=8212, UniqN=6889, UniqN1N=46)
    # 'resources/developed/sp18/sp18.tsv'   -----> counts of compounds with 'ind'/'coll'/'konvc'
    #           |     \__                         N1 meaning built from each N1 (UniqN1N=46)
    #           |        \__               'resources/developed/sp18/intpe/summaries/n1_sem.tsv'
    #           |           \___________ 
    #           |            __________/\________________ 
    #           |           /                            \   
    #           | + built from N1s appearing only        (+ built from N1s appearing only
    #           | with a Sg meaning (N=187, UniqN1N=1)         with a Pl meaning (N=0))
    #           |   'resources/developed/sp18/
    #           |   intpe/leftovers/nalt_sg.tsv'
    #           | 
    #           | 
    #  + built from N1s appearing both            Record of applicable N1-targeting constraints
    #  with a Sg and with a Pl meaning   ----->      for each unique N1 (UniqN1N=45)
    #  (N=8025, UniqN=6746, UniqN1N=45)          'resources/developed/sp18/intpe/
    # 'resources/developed/sp18/                     summaries/alt_constr.tsv'
    #     intpe/alt.tsv'    \    
    #           |            \______ 
    #           |                   \________
    #           |                            \
    #  + N1 may not attach                 + N1 may attach 
    #  a pluralic linker                    a pluralic linker     
    # (N=5311, UniqN=4449, UniqN1N=30)     (N=2714, UniqN1N=15)
    # 'resources/developed/sp18/          'resources/developed/sp18/
    # intpe/alt_npll.tsv'                 intpe/leftovers/alt_pll.tsv'


    sp18_path = "resources/developed/sp18/sp18.tsv"
    constr_path = "constraints/constraints_all_revised.yaml"

    outdir = "resources/developed/sp18/intpe"
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(os.path.join(outdir, "summaries"), exist_ok=True)
    os.makedirs(os.path.join(outdir, "leftovers"), exist_ok=True)

    outcsv_args = {
        "sep": "\t",
        "index": True,
        "header": True
    }


    # 1. Load SP18.
    
    # SP18 (N=8212, UniqN=6889, UniqN1N=46)
    sp18 = pd.read_csv(
        sp18_path,
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


    # 2. Load the constraints.

    with open(constr_path, encoding="utf-8") as f:
        constraints: dict = list(yaml.safe_load_all(f))[-1]["constraints"]


    # 3. Leave out compounds whose N1s do not exhibit an alternation between
    # Sg vs. Pl meaning.

    # Problematic group 1: if an N1 only occurred with either Sg or Pl meaning,
    # we cannot study its linker alternation across the meaning.

    # counts of compounds with 'ind'/'coll'/'konvc' N1 meaning
    # built from each N1
    # (UniqN1N=46)
    n1_sem_data = {
        const_comb: {
            n1_sem: len(group[group["n1_sem"] == n1_sem])
            for n1_sem in ["ind", "coll", "konvc"]
        }
        for const_comb, group in sp18.groupby("n1")
    }
    n1_sem = pd.DataFrame.from_dict(n1_sem_data, orient="index")
    n1_sem.to_csv(
        os.path.join(outdir, "summaries/n1_sem.tsv"),
        **outcsv_args
    )
    # we will use the lax annotation here
    n1_sem["coll-lax"] = n1_sem["coll"] + n1_sem["konvc"]

    # only Sg meaning (N=187, UniqN=143, UniqN1N=1)
    nalt_sg = n1_sem[n1_sem["coll-lax"] == 0].index
    sp18[sp18["n1"].isin(nalt_sg)].to_csv(
        os.path.join(outdir, "leftovers/nalt_sg.tsv"),
        **outcsv_args
    )

    # # only Pl meaning (N=0)
    # nalt_pl = n1_sem[n1_sem["ind"] == 0].index
    # sp18.loc[nalt_pl].to_csv(
    #     os.path.join(outdir, "leftovers/nalt_pl.tsv"),
    #     **outcsv_args
    # )

    # alternating forms (N=8025, UniqN=6746, UniqN1N=45)
    alt = sp18[
        ~sp18["n1"].isin(nalt_sg) # &
        # ~sp18.index.isin(nalt_pl)
    ]
    alt.to_csv(
        os.path.join(outdir, "alt.tsv"),
        **outcsv_args
    )


    # 4. Leave out compounds whose N1 may attach the pluralic linker
    # due to other constraints.

    # Problematic group 2.
    # As we know, semantic constraints are not the only constraints 
    # that govern linker choice. There may be cases where a constituent
    # with no IntPE will still consistently receive a pluralic linker (with no plural cue)
    # due to other constraints, e.g. phonological or morphological. 
    # We therefore expect to see the ExtPE (if it exists) more pronounced
    # in the compounds that may not insert the pluralic linker due to other constraints. 
    # Otherwise, the IntPE may be masked.
    # This is exemplified by the examples in the dataset of 
    # 'Katzenfell', 'Kinderbuch'.
    # Therefore, we will here separate the subset into the group
    # of compounds whose N1 may and may not insert a pluralic linker.

    # Note that rather than performing this analysis on the base
    # of empirical counts of compounds with pluralic vs. non-pluralic linkers
    # built from each N1, we will perform it on the base of potential
    # constraint applicability as defined by [shmalts_2026], using the
    # (corrected) applicability checkers originating form this works.
    # This will allow us to establish a theoretically grounded "ground truth"-like
    # set of compounds whose N1s "should" or "should not" 
    # insert a pluralic linker in the Sg form, and thus extract
    # the empirical difference caused by the colloquial speech 
    # in cases the empirical data does not match the theoretical expectation.

    # On top of targeting non-pluralic constraints only, we will also 
    # ignore L2P constraints that are irrelevant to the ExtPE, since they 
    # are not generative.
    # Note that since we are actually interested in constraints that assign 
    # a pluralic linker, most of the constraints whose checkers are not implemented 
    # at the time of this step (June 2026) are irrelevent anyways:
    # these are copulative, argumental compounds, technical terms, and a few other
    # constraints that assign -s- or a zero linker.
    # However, note that there are two non-pluralic constraints 
    # that assign a pluralic linker, but which are not implemented 
    # in the applicability checkers on the time of this step (June 2026),
    # and this is a **limitation** of the current analysis. These are:
    # * `p2l:decl_cl:pl:#e-0|msyl_anim-e` (assigns -e- to monosyllabic animal designations).
    # * `p2l:decl_cl:pl:#er-0/er|anim-er` (assigns -"er- to monosyllabic animal designations).

    def is_pll_acceptable(
        n1: str,
        pl_marker: str,
        pbar: tqdm
    ) -> Tuple[bool, str, str, str]:
        # we only check for the applicability of constraints on N1,
        # so we do not really need a real compound,
        # but we still need to create a Compound object to pass to the checkers
        comp = Compound(f"{n1}_maske")
        applicable_constr = []
        applicable_pl_constr = []
        all_acceptable_linkers = []
        for c_id, constraint in constraints.items():
            if (
                # non-pluralic constraints only
                constraint["is_pluralic"] or
                # ignore L2P
                ("linker" in constraint["appl_item"])
            ):
                continue
            func_name = constraint["func_alias"]
            if hasattr(applicability_checkers, func_name + "_is_applicable"):
                try:
                    is_applicable_func = getattr(
                        applicability_checkers,
                        func_name + "_is_applicable"
                    )
                    is_applicable = is_applicable_func(comp)
                    if is_applicable:
                        acceptable_linkers = constraint["acceptable_linkers"]
                        applicable_constr.append(c_id)
                        if pl_marker in acceptable_linkers:
                            applicable_pl_constr.append(c_id)
                        all_acceptable_linkers.extend(acceptable_linkers)
                except KeyError:
                    # unreliable, exclude
                    return None, None, None, None
        applicable_constr = ", ".join(applicable_constr)
        applicable_pl_constr = ", ".join(applicable_pl_constr)
        all_acceptable_linkers = ", ".join(set(all_acceptable_linkers))
        pbar.update(1)
        return (
            pl_marker in all_acceptable_linkers,
            all_acceptable_linkers,
            applicable_constr,
            applicable_pl_constr
        )

    # record applicable N1-targeting constraints for each unique N1
    # TODO: optimize
    alt_constr = alt.copy()	\
        [["n1", "n1_pl_marker"]]	\
        .reset_index(drop=True)	\
        .set_index("n1")
    # keep unique N1s
    alt_constr = alt_constr[
        ~alt_constr.index.duplicated(keep="first")
    ]
    
    with tqdm(
        total=len(alt_constr), 
        desc="Checking pluralic linker acceptability"
    ) as pbar:
        (
            alt_constr["is_pll_acceptable"],
            alt_constr["acceptable_linkers"],
            alt_constr["applicable_constr"],
            alt_constr["applicable_pl_constr"]
        ) = zip(
            *alt_constr.apply(
                lambda row: is_pll_acceptable(row.name, row["n1_pl_marker"], pbar),
                axis=1
            )
        )
    # (UniqN1N=45, one of them is NA since it is not in CELEX-nouns)
    alt_constr.to_csv(
        os.path.join(outdir, "summaries/alt_constr.tsv"),
        **outcsv_args
    )
    # replace NA with True to exclude those N1s from the analysis,
    # as we cannot reliably determine their acceptability
    alt_constr["is_pll_acceptable"] = (
        alt_constr["is_pll_acceptable"].fillna(True)
    )
    n1_pll = alt_constr[alt_constr["is_pll_acceptable"]].index

    # N1 may attach the pluralic linker
    # (N=2714, UniqN1N=15)
    alt[alt["n1"].isin(n1_pll)].to_csv(
        os.path.join(outdir, "leftovers/alt_pll.tsv"),
        **outcsv_args
    )

    # N1 may not attach the pluralic linker
    # (N=5311, UniqN=4449, UniqN1N=30)
    alt[~alt["n1"].isin(n1_pll)].to_csv(
        os.path.join(outdir, "alt_npll.tsv"),
        **outcsv_args
    )


if __name__ == "__main__":
    main()