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


# python3 -m data_utils.prepare_sp18_extpe
def main():

    # This script prepares the default version of SP18 dataset
    # with lemmatized compounds for investigation of the
    # external plural effect (ExtPE).
    #
    # Convention: (N=x) refers to the number of compound **tokens** in the dataset, 
    # (UniqN=x) refers to the number of unique compound **lemmata** in the dataset,
    # (UniqCN=x) refers to the number of unique constituent combinations
    # in the dataset (regardless of the linker),
    # (UniqN1N=x) refers to the number of N1 **lemmata** in the dataset.
    # 'Compounds' refers to 'compound tokens' unless specified otherwise.
    #
    # The default SP18 contains N=8212, UniqN=6889, UniqCN=6161, UniqN1N=46 lemmatized compounds
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

    # What I found unreasonable in Schäfer & Pankratz’s methodology 
    # regarding the ExtPE is that they ran the statistical tests 
    # over all the compounds in their original data. However, their data is full 
    # of interfering signals when it comes to the ExtPE. We detected three problematic
    # groups of compounds with this regard:
    # 1. Compounds that only appear in Sg or only in Pl form. Since the ExtPE
    # is triggered by grammatical Pl number of the entire compound,
    # this compound should occur both in Sg and in Pl form in order to
    # validate whether the ExtPE takes place. Otherwise, it is impossible
    # to make judgements about the expected behavior of these compounds
    # in the opposite number form.
    # 2. Compounds under the internal plural effect (IntPE). 
    # Since the IntPE works on a lexical level,
    # it should assign the pluralic linker in both Sg and Pl forms
    # (e.g. 'Äpfelkiste' vs. 'Äpfelkisten', or 'Liederabend' vs. 'Liederabende',
    # found in the data). Thus, the IntPE may interfere
    # with the ExtPE and make the latter undetectable.
    # 3. Compounds whose N1s may attach the pluralic linker due to
    # non-pluralic constraints, e.g. because of schwa ('Katzenfell' vs. 'Katzenfelle',
    # found in the data) or as a person designation ('Kinderbuch' vs. 'Kinderbücher',
    # found in the data). Again, if the given N1 mostly takes a pluralic linker 
    # in its Sg form, it will most likely do so in Pl, 
    # making the ExtPE undetectable.
    #
    # Our idea for investigating the ExtPE is, conversely, to confront
    # contrastive pairs of compounds resulting from the same constituent combination
    # in Sg and Pl forms (e.g. 'Apfel' + 'Baum' is 'Apfelbaum' in Sg, will it become
    # 'Äpfelbäume' in Pl?).
    # Thus, the main goal of this script is to detect and filter out these
    # problematic groups and extract the contrastive Sg-Pl pairs of identical
    # constituent combinations. However, each of the intermediate data collection
    # will also be saved in order to enable ablation studies on how
    # strongly each of this group interfere with the ExtPE.

    # The overall preprocessing includes the following:
    #   1. Load SP18.
    #   2. Load the constraints.
    #   3. Extract sets of multiple compounds with identical constituent combinations
    #   (regardless of the linker).
    #   4. Leave out compounds that do not exhibit an alternation between
    #   Sg vs. Pl forms.
    #   5. Leave out compounds under the IntPE.
    #   6. Leave out compounds whose N1 may attach the pluralic linker
    #   due to non-pluralic constraints.

    # As a result of the preprocessing, we obtain the following datasets
    # (all have the same notation as SP18):
    #
    #   * 'resources/developed/sp18/extpe/ident_cc_all.tsv'
    #   (N=3453, UniqN=2130, UniqCN=1402)
    #   Compounds built from non-unique constituent combinations (regardless 
    #   of the linker)
    #
    #
    #   * 'resources/developed/sp18/extpe/ic_alt.tsv'
    #   (N=2318, UniqN=1246, UniqCN=869)
    #   Compounds built from non-unique constituent combinations (regardless 
    #   of the linker) appearing both in the Sg and the Pl forms
    #
    #   * 'resources/developed/sp18/extpe/leftovers/ic_nalt_sg.tsv'
    #   (N=892)
    #   Compounds built from non-unique constituent combinations (regardless 
    #   of the linker) appearing only in the Sg form
    #
    #   * 'resources/developed/sp18/extpe/leftovers/ic_nalt_pl.tsv'
    #   (N=243)
    #   Compounds built from non-unique constituent combinations (regardless 
    #   of the linker) appearing only in the Pl form
    #
    #
    #   * 'resources/developed/sp18/extpe/ic_alt_nipe.tsv'
    #   (N=1931, UniqN=1043, UniqCN=724)
    #   Compounds built from non-unique constituent combinations (regardless 
    #   of the linker) appearing both in the Sg and the Pl forms
    #   and not undergoing the IntPE
    #
    #   * 'resources/developed/sp18/extpe/leftovers/ic_alt_ipe.tsv'
    #   (N=387)
    #   Compounds built from non-unique constituent combinations (regardless 
    #   of the linker) appearing both in the Sg and the Pl forms
    #   and undergoing the IntPE
    #
    #
    #   * 'resources/developed/sp18/extpe/ic_alt_nipe_npll.tsv'
    #   (N=1236, UniqN=665, UniqCN=468, UniqN1N=30)
    #   Compounds built from non-unique constituent combinations (regardless 
    #   of the linker) appearing both in the Sg and the Pl forms
    #   and not undergoing the IntPE whose N1 may not attach a pluralic linker
    #
    #   * 'resources/developed/sp18/extpe/leftovers/ic_alt_nipe_pll.tsv'
    #   (N=695, UniqN1N=16)
    #   Compounds built from non-unique constituent combinations (regardless 
    #   of the linker) appearing both in the Sg and the Pl forms
    #   and not undergoing the IntPE whose N1 may attach a pluralic linker
    #
    #
    #
    #   * 'resources/developed/sp18/extpe/summaries/ic_nums.tsv'
    #   (UniqCN=1402)
    #   Counts of compounds in the Sg/Pl forms built from each constituent combination
    #   (from 'resources/developed/sp18/extpe/ident_cc_all.tsv')
    #
    #   * 'resources/developed/sp18/extpe/summaries/ic_n1_sem.tsv'
    #   (UniqCN=869)
    #   Counts of compounds with 'ind'/'coll'/'konvc' N1 meaning 
    #   built from each constituent combination
    #   (from 'resources/developed/sp18/extpe/ic_alt.tsv')
    #
    #   * 'resources/developed/sp18/extpe/summaries/ic_alt_nipe_constr.tsv'
    #   (UniqN1N=46)
    #   Record of applicable N1-targeting constraints for each unique N1
    #   (from 'resources/developed/sp18/extpe/ic_alt_nipe.tsv')

    # Thus, the data tree looks as follows:
    #
    #          SP18
    #   lemmatized compounds
    # (N=8212, UniqN=6889, UniqCN=6161, UniqN1N=46)
    # 'resources/developed/sp18/sp18.tsv'
    #           |                    \__
    #           |                       \_____
    #           |                             \
    #  compounds from non-unique              removed compounds
    #  constituent combinations                 from unique constituent
    #  (N=3453, UniqN=2130, UniqCN=1402)          combinations (N=4669)
    # 'resources/developed/sp18/
    # extpe/ident_cc_all.tsv' -----> counts of compounds in the Sg/Pl forms
    #           |     \__                       built from each constituent combination (UniqCN=1402)
    #           |        \__               'resources/developed/sp18/extpe/summaries/ic_nums.tsv'
    #           |           \___________ 
    #           |            __________/\_________ 
    #           |           /                     \   
    #           |   + appearing only               + appearing only
    #           |   in the Sg form (N=892)         in the Pl form (N=243)
    #           |   'resources/developed/sp18/      'resources/developed/sp18/
    #           | extpe/leftovers/ic_nalt_sg.tsv'    extpe/leftovers/ic_nalt_pl.tsv'
    #           |                     
    #           | 
    #  + appearing both                            
    #  in the Sg and the Pl forms            counts of compounds with 'ind'/'coll'/'konvc' N1 meaning
    #  (N=2318, UniqN=1246, UniqCN=869) ----->  built from each constituent combination (UniqCN=869)
    # 'resources/developed/sp18/           'resources/developed/sp18/extpe/summaries/ic_n1_sem.tsv'
    #    extpe/ic_alt.tsv'     \_____
    #           |                    \__
    #           |                       \_____
    #           |                             \
    #           |               + undergoing the IntPE (N=387)
    #           |         'resources/developed/sp18/extpe/leftovers/ic_alt_ipe.tsv'
    #           |
    #           |
    #  + not undergoing the IntPE               Record of applicable N1-targeting constraints
    #  (N=1931, UniqN=1043, UniqCN=724) ----->      for each unique N1 (UniqN1N=46)
    # 'resources/developed/sp18/                  'resources/developed/sp18/extpe/
    #     extpe/ic_alt_nipe.tsv'                  summaries/ic_alt_nipe_constr.tsv'
    #           |                    \__
    #           |                       \_____
    #           |                             \
    #  + N1 may not attach                 + N1 may attach 
    #  a pluralic linker                    a pluralic linker     
    #   (N=1236, UniqN=665,                   (N=695, UniqN1N=16)
    #  UniqCN=468, UniqN1N=30)               'resources/developed/sp18/
    # 'resources/developed/sp18/              extpe/leftovers/ic_alt_nipe_pll.tsv'
    # extpe/ic_alt_nipe_npll.tsv'         


    sp18_path = "resources/developed/sp18/sp18.tsv"
    constr_path = "constraints/constraints_all_revised.yaml"

    outdir = "resources/developed/sp18/extpe"
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(os.path.join(outdir, "summaries"), exist_ok=True)
    os.makedirs(os.path.join(outdir, "leftovers"), exist_ok=True)

    outcsv_args = {
        "sep": "\t",
        "index": True,
        "header": True
    }


    # 1. Load SP18.
    
    # SP18 (N=8212, UniqN=6889, UniqCN=6161, UniqN1N=46)
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


    # 3. Extract sets of multiple compounds with identical constituent combinations
    # (regardless of the linker).

    # All compounds whose constituent combination is unique in the data will be
    # filtered out as they cannot build a contrastive pair.

    # non-unique constituent combinations (N=3453, UniqN=2130, UniqCN=1402)
    sp18["const_comb"] = sp18["n1"] + "+" + sp18["n2"]
    ident_cc_all = sp18[sp18.duplicated(subset="const_comb", keep=False)]    \
        .sort_values("const_comb")  \
        .reset_index(drop=False)    \
        .set_index("const_comb")
    ident_cc_all.to_csv(
        os.path.join(outdir, "ident_cc_all.tsv"),
        **outcsv_args
    )


    # 4. Leave out compounds that do not exhibit an alternation between
    # Sg vs. Pl forms.

    # Problematic group 1: if a compound only occurred in either Sg or Pl form,
    # we cannot study its linker alternation across the numbers.

    # counts of compounds in the Sg/Pl forms built
    # from each constituent combination
    # (UniqCN=1402)
    ic_nums_data = {
        const_comb: {
            "sg_form": len(group[group["n2_num"] == "sg"]),
            "pl_form": len(group[group["n2_num"] == "pl"])
        }
        for const_comb, group in ident_cc_all.groupby("const_comb")
    }
    ic_nums = pd.DataFrame.from_dict(ic_nums_data, orient="index")
    ic_nums.to_csv(
        os.path.join(outdir, "summaries/ic_nums.tsv"),
        **outcsv_args
    )

    # only Sg forms (N=892)
    ic_nalt_sg = ic_nums[ic_nums["pl_form"] == 0].index
    ident_cc_all.loc[ic_nalt_sg].to_csv(
        os.path.join(outdir, "leftovers/ic_nalt_sg.tsv"),
        **outcsv_args
    )

    # only Pl forms (N=243)
    ic_nalt_pl = ic_nums[ic_nums["sg_form"] == 0].index
    ident_cc_all.loc[ic_nalt_pl].to_csv(
        os.path.join(outdir, "leftovers/ic_nalt_pl.tsv"),
        **outcsv_args
    )

    # alternating forms (N=2318, UniqN=1246, UniqCN=869)
    ident_const_alt = ident_cc_all[
        ~ident_cc_all.index.isin(ic_nalt_sg) &
        ~ident_cc_all.index.isin(ic_nalt_pl)
    ]
    ident_const_alt.to_csv(
        os.path.join(outdir, "ic_alt.tsv"),
        **outcsv_args
    )


    # 5. Leave out compounds under the IntPE.

    # Problematic group 2.
    # We assume that since in standard (not colloquial)
    # German, the combination of N1 and the linker should
    # remain the same in Sg and Pl compound form,
    # (e.g. Apfelbaum vs. Apfelbäume),
    # and since the  should enforce
    # the pluralic linker, nouns that undergo the
    #  may not exhibit a reliable
    # alternation in Sg vs. Pl forms, since they would
    # receive the pluralic linker in its base form (Sg)
    # and bring it to the Pl form. This is exemplified 
    # by the examples in the dataset of Äpfelkiste vs. Äpfelkisten,
    # or Liederabend vs. Liederabende.
    # We therefore further separate the data onto the subsets
    # of alternating compounds with no 
    # and those with the .
    # 
    # Please note that a few constituent combinations exhibit
    # variation between Sg and Pl-like meaning of N1
    # in different entries depending on the context (refer to the dataset).
    # These are:
    # 'bett+belegung', 'bucht+system', 'ei+paket',
    # 'ei+sack', 'element+häufigkeit', 'element+zuordnung', 'gerät+verlust',
    # 'hand+kontakt', 'hund+buch', 'kind+haus', 'kommune+bewegung',
    # 'kommune+tag', 'lied+abend', 'mutter+zentrum', 'nation+tafel',
    # 'schloss+tour', 'schwester+genossenschaft', 'stadt+tour', 'vater+zentrum',
    # 'vogel+buch', 'vogel+population', 'vogel+zimmer', 'zahn+differenz'.
    # 
    # Since, again, this difference points to the IntPE rather than 
    # the ExtPE, we exclude these combinations from the analysis of the ExtPE.

    # counts of compounds with 'ind'/'coll'/'konvc' N1 meaning
    # built from each constituent combination
    ic_n1_sem_data = {
        const_comb: {
            n1_sem: len(group[group["n1_sem"] == n1_sem])
            for n1_sem in ["ind", "coll", "konvc"]
        }
        for const_comb, group in ident_const_alt.groupby("const_comb")
    }
    ic_n1_sem = pd.DataFrame.from_dict(ic_n1_sem_data, orient="index")
    ic_n1_sem.to_csv(
        os.path.join(outdir, "summaries/ic_n1_sem.tsv"),
        **outcsv_args
    )
    ic_n1_sem_share_ind = ic_n1_sem["ind"] / ic_n1_sem.sum(axis=1)

    # IntPE (N=387)
    ic_n1_sem_non_ind = ic_n1_sem_share_ind[ic_n1_sem_share_ind < 1].index
    ident_const_alt.loc[ic_n1_sem_non_ind].to_csv(
        os.path.join(outdir, "leftovers/ic_alt_ipe.tsv"),
        **outcsv_args
    )

    # no IntPE (N=1931, UniqN=1043, UniqCN=724)
    ic_alt_nipe = ident_const_alt[
        ~ident_const_alt.index.isin(ic_n1_sem_non_ind)
    ]
    ic_alt_nipe.to_csv(
        os.path.join(outdir, "ic_alt_nipe.tsv"),
        **outcsv_args
    )


    # 6. Leave out compounds whose N1 may attach the pluralic linker
    # due to other constraints.

    # Problematic group 3.
    # As we know, semantic constraints are not the only constraints 
    # that govern linker choice. There may be cases where a constituent
    # with no ExtPE will still consistently receive a pluralic linker (with no plural cue)
    # due to other constraints, e.g. phonological or morphological. 
    # Since a compound with a pluralic linker in Sg will most probably appear 
    # with the same linker in Pl (see the explanation above), we expect to see 
    # the ExtPE (if it exists) only in the compounds that may not insert 
    # the pluralic linker the their lemmatized (hence, also Sg) form. 
    # Otherwise, if the compound inserts the pluralic linker (in the Sg form), 
    # the chances are that it will also  insert the pluralic linker in the Pl form, 
    # and thus the ExtPE will be masked.
    # This is exemplified by the examples in the dataset of 
    # 'Katzenfell' vs. 'Katzenfelle', 'Kinderbuch' vs. 'Kinderbücher'.
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
    ic_alt_nipe_constr = ic_alt_nipe.copy()	\
        [["n1", "n1_pl_marker"]]	\
        .reset_index(drop=True)	\
        .set_index("n1")
    # keep unique N1s
    ic_alt_nipe_constr = ic_alt_nipe_constr[
        ~ic_alt_nipe_constr.index.duplicated(keep="first")
    ]
    
    with tqdm(
        total=len(ic_alt_nipe_constr), 
        desc="Checking pluralic linker acceptability"
    ) as pbar:
        (
            ic_alt_nipe_constr["is_pll_acceptable"],
            ic_alt_nipe_constr["acceptable_linkers"],
            ic_alt_nipe_constr["applicable_constr"],
            ic_alt_nipe_constr["applicable_pl_constr"]
        ) = zip(
            *ic_alt_nipe_constr.apply(
                lambda row: is_pll_acceptable(row.name, row["n1_pl_marker"], pbar),
                axis=1
            )
        )
    # (UniqN1N=46, one of them is NA since it is not in CELEX-nouns)
    ic_alt_nipe_constr.to_csv(
        os.path.join(outdir, "summaries/ic_alt_nipe_constr.tsv"),
        **outcsv_args
    )
    # replace NA with True to exclude those N1s from the analysis,
    # as we cannot reliably determine their acceptability
    ic_alt_nipe_constr["is_pll_acceptable"] = (
        ic_alt_nipe_constr["is_pll_acceptable"].fillna(True)
    )
    n1_pll = ic_alt_nipe_constr[ic_alt_nipe_constr["is_pll_acceptable"]].index

    # N1 may attach the pluralic linker
    # (N=695, UniqN1N=16)
    ic_alt_nipe[ic_alt_nipe["n1"].isin(n1_pll)].to_csv(
        os.path.join(outdir, "leftovers/ic_alt_nipe_pll.tsv"),
        **outcsv_args
    )

    # N1 may not attach the pluralic linker
    # (N=1236, UniqN=665, UniqCN=468, UniqN1N=30)
    ic_alt_nipe[~ic_alt_nipe["n1"].isin(n1_pll)].to_csv(
        os.path.join(outdir, "ic_alt_nipe_npll.tsv"),
        **outcsv_args
    )


if __name__ == "__main__":
    main()