# prerequisites: 'data_utils/prepare_sp18.py' has been run, 
# and the output of that script is available in 'resources/developed/sp18'.

import os
import pandas as pd
from collections import defaultdict


def main():

    # This script prepares the default version of SP18 dataset
    # with lemmatized compounds for investigation of the
    # external plural effect (ExtPE).
    #
    # Convention: (N=x) refers to the number of compound **tokens** in the dataset, 
    # (UniqN=x) refers to the number of compound **types** in the dataset,
    # (UniqCN=x) refers to the number of constituent combination **types**
    # in the dataset (regardless of the linker),
    # (UniqN1N=x) refers to the number of N1 **types** in the dataset.
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
    # 3. Compounds whose N1s are forced to attach the pluralic linker 
    # due to other constraints, e.g. because of schwa ('Katzenfell' vs. 'Katzenfelle',
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
    #   2. Extract sets of multiple compounds with identical constituent combinations
    #   (regardless of the linker).
    #   3. Leave out compounds that do not exhibit an alternation between
    #   Sg vs. Pl forms.
    #   4. Leave out compounds under the IntPE.
    #   5. Leave out compounds whose N1 mostly attaches the pluralic linker
    #   due to other constraints.

    # As a result of the preprocessing, we obtain the following datasets
    # (all have the same notation as SP18):
    #
    #   * 'resources/developed/sp18/external_effect/ident_const_all.tsv'
    #   (N=3453, UniqN=2130, UniqCN=1402)
    #   Compounds built from non-unique constituent combinations (regardless 
    #   of the linker)
    #
    #
    #   * 'resources/developed/sp18/external_effect/ic_alt_all.tsv'
    #   (N=2318, UniqN=1246, UniqCN=869)
    #   Compounds built from non-unique constituent combinations (regardless 
    #   of the linker) appearing both in the Sg and the Pl forms
    #
    #   * 'resources/developed/sp18/external_effect/leftovers/ic_nalt_sg.tsv'
    #   (N=892)
    #   Compounds built from non-unique constituent combinations (regardless 
    #   of the linker) appearing only in the Sg form
    #
    #   * 'resources/developed/sp18/external_effect/leftovers/ic_nalt_pl.tsv'
    #   (N=243)
    #   Compounds built from non-unique constituent combinations (regardless 
    #   of the linker) appearing only in the Pl form
    #
    #
    #   * 'resources/developed/sp18/external_effect/ic_alt_nipe.tsv'
    #   (N=1931, UniqN=1043, UniqCN=724)
    #   Compounds built from non-unique constituent combinations (regardless 
    #   of the linker) appearing only in the Sg form and not undergoing the IntPE
    #
    #   * 'resources/developed/sp18/external_effect/leftovers/ic_alt_ipe.tsv'
    #   (N=387)
    #   Compounds built from non-unique constituent combinations (regardless 
    #   of the linker) appearing only in the Sg form and undergoing the IntPE
    #
    #
    #   * 'resources/developed/sp18/external_effect/ic_alt_nipe_sg_l.tsv'
    #   (N=1560, UniqN=842, UniqCN=590, UniqN1N=37)
    #   Compounds built from non-unique constituent combinations (regardless 
    #   of the linker) appearing only in the Sg form and not undergoing the IntPE
    #   whose N1 mostly attach a non-pluralic linker in the Sg form
    #
    #   * 'resources/developed/sp18/external_effect/leftovers/ic_alt_nipe_pl_l.tsv'
    #   (N=371, UniqN1N=9)
    #   Compounds built from non-unique constituent combinations (regardless 
    #   of the linker) appearing only in the Sg form and not undergoing the IntPE
    #   whose N1 mostly attach the pluralic linker in the Sg form
    #
    #
    #   
    #   * 'resources/developed/sp18/external_effect/summaries/ic_nums.tsv'
    #   (UniqCN=1402)
    #   Counts of compounds in the Sg/Pl forms built from each constituent combination
    #   (from 'resources/developed/sp18/external_effect/ident_const_all.tsv')
    #
    #   * 'resources/developed/sp18/external_effect/summaries/ic_n1_sem.tsv'
    #   (UniqCN=869)
    #   Counts of compounds with 'ind'/'coll'/'konvc' N1 meaning built from each constituent combination
    #   (from 'resources/developed/sp18/external_effect/ic_alt_all.tsv')
    #
    #   * 'resources/developed/sp18/external_effect/summaries/ic_alt_nipe_sg_links.tsv'
    #   (UniqN1N=46)
    #   Counts of compounds with pluralic and non-pluralic linkers built with each N1
    #   (from 'resources/developed/sp18/external_effect/ic_alt_nipe.tsv')

    # Thus, the data tree looks as follows:
    #
    #          SP18
    #   lemmatized compounds
    #   (N=8212, UniqN=6889)
    # 'resources/developed/sp18/sp18.tsv'
    #           |                    \__
    #           |                       \_____
    #           |                             \
    #  compounds from non-unique              removed compounds
    #  constituent combinations                 from unique constituent
    #  (N=3453, UniqN=2130, UniqCN=1402)          combinations (N=4669)
    # 'resources/developed/sp18/
    # external_effect/ident_const_all.tsv' -----> counts of compounds in the Sg/Pl forms
    #           |     \__                       built from each constituent combination (UniqCN=1402)
    #           |        \__               'resources/developed/sp18/external_effect/summaries/ic_nums.tsv'
    #           |           \___________ 
    #           |            __________/\_________ 
    #           |           /                     \   
    #           |   + appearing only               + appearing only
    #           |   in the Sg form (N=892)         in the Pl form (N=243)
    #           |   'resources/developed/sp18/     'resources/developed/sp18/
    #           |    external_effect/leftovers/    external_effect/leftovers/
    #           |    ic_nalt_sg.tsv'                 ic_nalt_pl.tsv'
    #           | 
    #           | 
    #  + appearing both                            
    #  in the Sg and the Pl forms            counts of compounds with 'ind'/'coll'/'konvc' N1 meaning
    #  (N=2318, UniqN=1246, UniqCN=869) ----->  built from each constituent combination (UniqCN=869)
    # 'resources/developed/sp18/           'resources/developed/sp18/external_effect/summaries/ic_n1_sem.tsv'
    # external_effect/ic_alt_all.tsv'
    #           |                    \__
    #           |                       \_____
    #           |                             \
    #           |               + undergoing the IntPE (N=387)
    #           |               'resources/developed/sp18/external_effect/leftovers/ic_alt_ipe.tsv'
    #           |
    #           |
    #  + not undergoing the IntPE                  Counts of compounds with pluralic and 
    #  (N=1931, UniqN=1043, UniqCN=724) ----->  non-pluralic linkers built from each N2 (UniqN1N=46)
    # 'resources/developed/sp18/                  'resources/developed/sp18/external_effect/
    # external_effect/ic_alt_nipe.tsv'              summaries/ic_alt_nipe_sg_links.tsv'
    #           |                    \__
    #           |                       \_____
    #           |                             \
    #  + mostly attach a non-             + mostly attach the pluralic
    #  linker in the Sg form               linker in the Sg form
    #  (N=1560, UniqN=842,                  (N=371, UniqN1N=9)
    #  UniqCN=590, UniqN1N=37)                'resources/developed/sp18/
    # 'resources/developed/sp18/              external_effect/leftovers/ic_alt_nipe_pl_l.tsv'
    # external_effect/ic_alt_nipe_sg_l.tsv'     


    sp18_path = "resources/developed/sp18/sp18.tsv"

    outdir = "resources/developed/sp18/external_effect"

    outcsv_args = {
        "sep": "\t",
        "index": True,
        "header": True
    }


    # 1. Load SP18.
    
    # SP18 (N=8212, UniqN=6889)
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


    # 2. Extract sets of multiple compounds with identical constituent combinations
    # (regardless of the linker).

    # All compounds whose constituent combination is unique in the data will be
    # filtered out as they cannot build a contrastive pair.

    # non-unique constituent combinations (N=3453, UniqN=2130, UniqCN=1402)
    sp18["const_comb"] = sp18["n1"] + "+" + sp18["n2"]
    ident_const_all = sp18[sp18.duplicated(subset="const_comb", keep=False)]    \
        .sort_values("const_comb")  \
        .reset_index(drop=False)    \
        .set_index("const_comb")
    ident_const_all.to_csv(
        os.path.join(outdir, "ident_const_all.tsv"),
        **outcsv_args
    )


    # 3. Leave out compounds that do not exhibit an alternation between
    # Sg vs. Pl forms.

    # Problematic group 1: if a compound only occurred in either Sg or Pl form,
    # we cannot study its linker alternation across the numbers.

    # counts of compounds in the Sg/Pl forms built
    # from each constituent combination
    ic_nums_data = {
        const_comb: {
            "sg_form": len(group[group["n2_num"] == "sg"]),
            "pl_form": len(group[group["n2_num"] == "pl"])
        }
        for const_comb, group in ident_const_all.groupby("const_comb")
    }
    ic_nums = pd.DataFrame.from_dict(ic_nums_data, orient="index")
    ic_nums.to_csv(
        os.path.join(outdir, "summaries/ic_nums.tsv"),
        **outcsv_args
    )

    # only Sg forms (N=892)
    ic_nalt_sg = ic_nums[ic_nums["pl_form"] == 0].index
    ident_const_all.loc[ic_nalt_sg].to_csv(
        os.path.join(outdir, "leftovers/ic_nalt_sg.tsv"),
        **outcsv_args
    )

    # only Pl forms (N=243)
    ic_nalt_pl = ic_nums[ic_nums["sg_form"] == 0].index
    ident_const_all.loc[ic_nalt_pl].to_csv(
        os.path.join(outdir, "leftovers/ic_nalt_pl.tsv"),
        **outcsv_args
    )

    # alternating forms (N=2318, UniqN=1246, UniqCN=869)
    ident_const_alt = ident_const_all[
        ~ident_const_all.index.isin(ic_nalt_sg) &
        ~ident_const_all.index.isin(ic_nalt_pl)
    ]
    ident_const_alt.to_csv(
        os.path.join(outdir, "ic_alt_all.tsv"),
        **outcsv_args
    )


    # 4. Leave out compounds under the IntPE.

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


    # 5. Leave out compounds whose N1 mostly attaches the pluralic linker
    # due to other constraints.

    # Problematic group 3.
    # As we know, semantic constraints are not the only constraints 
    # that govern linker choice. There may be cases where a constituent
    # with no  may still consistently receive a pluralic linker (with no plural cue)
    # due to other constraints, e.g. phonological or morphological. 
    # Since a compound with a pluralic linker in Sg will most probably appear 
    # with the same linker in Pl (see the explanation above), we expect to see 
    # the ExtPE (if it exists) only in the compounds that usually take 
    # a zero linker in the Sg form. Otherwise, if the compound usually takes 
    # a pluralic linker in the Sg form, the chances are that it will also 
    # take a pluralic linker in the Pl form, and thus the ExtPE will be masked.
    # This is exemplified by the examples in the dataset of 
    # 'Katzenfell' vs. 'Katzenfelle', 'Kinderbuch' vs. 'Kinderbücher'.
    # Therefore, we will here separate the subset into the group
    # of compounds whose N1 mostly takes a zero linker in the Sg form
    # and the group of compounds whose N1 mostly takes a pluralic linker in teh Sg form.

    # count compounds with pluralic and non-pluralic linkers built with each N1
    ic_alt_nipe_sg_links_data = {
        const_comb: {
            "sg_l": len(group[
                (group["n2_num"] == "sg") &
                (~group["is_linker_pl"])
            ]),
            "pl_l": len(group[
                (group["n2_num"] == "sg") &
                (group["is_linker_pl"])
            ])
        }
        for const_comb, group in ic_alt_nipe.groupby("n1")
    }

    # (UniqN1N=46)
    ic_alt_nipe_sg_links = pd.DataFrame.from_dict(ic_alt_nipe_sg_links_data, orient="index")
    ic_alt_nipe_sg_links.to_csv(
        os.path.join(outdir, "summaries/ic_alt_nipe_sg_links.tsv"),
        **outcsv_args
    )

    # mostly pluralic linker in the Sg form (N=371, UniqN1N=9)
    ic_alt_nipe_pl_l = ic_alt_nipe_sg_links[
        ic_alt_nipe_sg_links["pl_l"] >
        ic_alt_nipe_sg_links["sg_l"]
    ].index
    ic_alt_nipe[ic_alt_nipe["n1"].isin(ic_alt_nipe_pl_l)].to_csv(
        os.path.join(outdir, "leftovers/ic_alt_nipe_pl_l.tsv"),
        **outcsv_args
    )

    # compounds with N1s that mostly attach a non-pluralic linker 
    # in the Sg form (N=1560, UniqN=842, UniqCN=590, UniqN1N=37)
    ic_alt_nipe_sg_l = ic_alt_nipe[
        ~ic_alt_nipe["n1"].isin(ic_alt_nipe_pl_l)
    ]
    ic_alt_nipe_sg_l.to_csv(
        os.path.join(outdir, "ic_alt_nipe_sg_l.tsv"),
        **outcsv_args
    )


if __name__ == "__main__":
    main()