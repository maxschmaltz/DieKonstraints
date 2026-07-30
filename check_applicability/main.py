# Prerequisites: prepare_celex_gecodb.py has been run and prepared CELEX and GeCoDB_v07 data is available.
#                prepare_sp18.py and prepare_sp18_pl_constr.py have been run and prepare SP18_Pl_Constr data is available.


import os
import zipfile
import numpy as np
import pandas as pd
import yaml
import copy
from collections import defaultdict
from tqdm import tqdm

# python3 -m check_applicability.main
from data_utils.gecodb_compound_parser import Compound
from data_utils import load_datasets
from . import applicability_checkers
from .regularity_scale import REGULARITY_SCALE


def main():
    
    constr_path = "constraints/constraints_all_revised.yaml"
    resdir = "out/constraints/applicability_statistics"

    save_tsv = lambda df, path: df.to_csv(
        path,
        sep="\t",
        header=True,
        index=True
    )

    # load constraints and dataset specs
    with open(constr_path, encoding="utf-8") as f:
        yamls = list(yaml.safe_load_all(f))
        constraints: dict = yamls[-1]["constraints"]
        constr_ids = list(constraints.keys())
        data_specs: dict = yamls[-2]["datasets"]

    # load datasets
    datasets = {
        dname: getattr(load_datasets, d["load_func"])(d["filepath"])
        for dname, d in data_specs.items()
    }

    all_appl_statistics = {}

    # We measure the coverage and regularity of different constraints on different
    # datasets. For each dataset, we follow the algorithm:
    # 1. For each constraint for each compound in the dataset,
    #   1.1. Check if the constraint has to be measured over this dataset; skip otherwise.
    #   1.2. Check if the constraint is implemented; skip otherwise.
    #   1.3. Extract the application item of the constraint in the compound (N1, N1+sem, N1+N2 etc.)
    #   1.4. Check whether the constraint is potentially applicable to the compound.
    #   Record results for further compounds with the same application item.
    #   1.5. If the constraint is potentially applicable to the compound,
    #   check whether the constraint actually applies.
    # 2. Calculate statistics over the dataset:
    #   2.1. Type coverage: proportion of the number of compounds for which the
    #   constraint is potentially applicable, and the total number of the compounds.
    #   2.2. Item coverage: proportion of the number of application items for which the
    #   constraint is potentially applicable, and the total number of the application items.
    #   2.3. Type regularity: proportion of the number of compounds to which
    #   the constraint applies, and the number of the covered compounds.
    #   2.4. Item regularity: average cross-item type regularity.
    #   Estimates the type regularity within each application item (mostly N1)
    #   and then average these estimates over all covered items. This is done to handle cases
    #   when a small portion of (very) productive items consistently violate a constrain,
    #   resulting is a huge disbalance in type regularity.
    #   E.g. in `p2l:drv:deadj_schwa$-0/en`, all 555 out of 4214 compounds
    #   that violated the constraint were constituted by a single N1 'Liebe'; thus,
    #   even one single N1 sank the type regularity to 0.868.
    #   2.5. Determine the support level of the constraint by the dataset.
    # 3. Save results.

    # For each dataset, we follow the algorithm:
    for dname, dataset in datasets.items():

        # init checkers with the correct CELEX-nouns version;
        # otherwise, older datasets may have items that are missing
        # in newer CELEX-nouns
        celexn_version = data_specs[dname]["celexn_version"]
        # this will load the correct version of CELEX-nouns
        # in the module for the functions to be referencing;
        # dedicated test confirmed that different CELEX-Nouns versions
        # are loaded for different datasets, and the functions
        # work differently in a corresponding way
        # (e.g. CELEX-Nouns v0 has N1 'Beamte', and CELEX-Nouns v1 does not,
        # so `schwa_fin_is_applicable` works fine with GeCoDB_v06 which
        # requires CELEX-Nouns v0 but throws a KeyError with
        # GeCoDB_v07 which requires CELEX-Nouns v1)
        applicability_checkers.__init__(celexn_version)

        # initialize indices; since the operations are symbolic and therefore
        # very fast, we do not create any cache or anything;
        # in case of any changes, the whole thing should be rerun and rebuilt
        # to ensure no outdated infos
        appl_index = pd.DataFrame(
            index=dataset.index,
            columns=[
                c for constr_id in constr_ids
                for c in [
                    # item is recorded to measure item cvg and reg
                    # conveniently in 2.2, 2.4
                    constr_id + "_item",
                    constr_id + "_is_applicable",
                    constr_id + "_applies"
                ]
            ]
        )
        appl_index.index.name = "comp_gecodb"

        is_appl_cache = defaultdict(dict)


        appl_statistics = pd.DataFrame(
            index=pd.Series(constr_ids, name="constr_id"),
            columns=[
                "appl_item",
                "n_appl_items",
                "quantifier",
                "cvg_item_abs",
                "cvg_item",
                "cvg_type",
                "reg_item",
                "reg_type",
                "n_violations",
                "is_productive",
                "is_regular",
                "expected_reg_level",
                "actual_reg_level",
                "support_level"
            ]
        )

        N = len(dataset)

        print(f"Measuring constraints over {dname}...\n\n".upper())
        for c_id, constraint in constraints.items():

            # read required properties
            appl_item = constraint["appl_item"]
            datasets_n_appl_items = constraint["datasets_n_appl_items"]
            func_name = constraint["func_alias"]
            quantifier = constraint["quantifier"]
            is_l2p = c_id.startswith("l2p")

            # 1.1. Check if the constraint has to be measured 
            # over this dataset; skip otherwise.
            if dname not in datasets_n_appl_items:
                print(f"{c_id} is not measured over this dataset.\n")
                continue


            # 1.2. Check if the constraint is implemented; skip otherwise.
            if not hasattr(applicability_checkers, func_name + "_is_applicable"):
                print(f"Checkers for {c_id} not implemented.\n")
                continue


            # wrapper
            is_applicable_func = getattr(
                applicability_checkers,
                func_name + "_is_applicable"
            )
            is_applied_func = getattr(
                applicability_checkers,
                func_name + "_applies"
            )

            pbar = tqdm(dataset.index, desc=f"Measuring {c_id}...")
            def _measure_constraint(row: pd.Series) -> tuple[str, bool, bool]:

                comp_gecodb = row.name

                # parse compound & its properties;
                # configure arguments for 1.4 and 1.5
                comp: Compound = Compound(comp_gecodb)
                n1 = comp.constituents[0].morph
                n2 = comp.constituents[1].morph
                linker = ("\"" if (l := comp.linkers[0]).adds_umlaut else "") + l.morph
                # the semantic plurality of N1 is determined
                # differently, depending on the dataset
                match dname:
                    case "sp18_pl_constr":
                        # While annotating the Pl meaning of N1s, Schäfer & Pankratz 2018
                        # found a number of uncertain examples, so they made two measurements:
                        # a strict measurement (the uncertain cases were treated as a Sg N1 meaning) 
                        # and a lax measurement (the uncertain cases were treated as a Pl N1 meaning).
                        # The experiment revealed that the difference between the two measurements 
                        # is negligible (see Schäfer & Pankratz 2018, 29), and the lax measurement 
                        # brings more positive result. We therefore conduct our own experiments
                        # in the strict paradigm.
                        is_n1sem_pl = row["n1_sem"] == "coll"
                        # _is_applicable P2L functions require the `is_n1sem_pl` parameter,
                        # _applies P2L function require the `is_linker_pl` parameter;
                        # checkers for the L2P function swap these two params
                        args_sem = (comp, is_n1sem_pl)
                        args_linker = (comp, row["is_linker_pl"])
                        args_is_applicable = args_sem if not is_l2p else args_linker
                        args_applies = args_linker if not is_l2p else args_sem
                    case _:
                        is_n1sem_pl = None
                        args_is_applicable = (comp, )
                        args_applies = (comp, )


                # 1.3. Extract the application item of the constraint 
                # in the compound (N1, N1+sem, N1+N2 etc.)
                # There are a few possibilities:
                #   * N1. Linguistic properties of the first constituent only.
                #   This is the case for the majority of the constraints.
                #   * N1 + N2. Linguistic properties of both constituents (`p2l:sem:2const_anim/pers-s`),
                #   or the semantic relation between the two constituents (`p2l:sem:comp_type:copula-0`,
                #   `p2l:sem:comp_type:arg-s`).
                #   * N1 + semantic plurality. Linguistic properties of the first constituent only
                #   and its semantic plurality (singular/plural). Application item for the pluralic
                #   constraints. Semantic plurality is carried out from the set of linguistic properties
                #   because it is variable (as opposed to, e.g., animacy). For example, 'Buch' + 'Deckel'
                #   wouldn't be potentially applicable for a pluralic constraint because 'Buch' has
                #   a singular meaning in this compound, while in 'Buch' + 'Sammlung' it would
                #   because of its plural meaning.
                #   * N1 + linker.
                #   * Compound. For the L2P constraints that require a certain linker to be in place.
                #   For example, any compound with N1 'Mutter' will be covered by
                #   `p2l:decl_cl:pl:#0_uml-0|def-0` but only that compound where N1 'Mutter'
                #   attaches an `_+=_` will be covered by for `l2p:0_uml`.

                match appl_item:
                    case "n1":
                        item = n1
                    case "n1+n2":
                        item = f"{n1}+{n2}"
                    case "n1+sem":
                        # for now, is only defined over the sp18_pl_constr
                        # dataset, which is handled above
                        if is_n1sem_pl is None:
                            raise
                        suffix = "plsem" if is_n1sem_pl else "sgsem"
                        item = f"{n1}+{suffix}"
                    case "n1+linker":
                        item = f"{n1}+{linker}"
                    case "compound":
                        item = comp.gecodb

                
                # 1.4. Check whether the constraint is potentially applicable to the compound.
                # Record results for further compounds with the same application item.
                
                if is_appl_cache.get(item, {}).get(c_id):
                    is_applicable = is_appl_cache[item][c_id]
                else:
                    is_applicable = is_applicable_func(*args_is_applicable)
                    if appl_item not in ["n1+n2", "compound"]:
                        # save repeated items
                        is_appl_cache[item][c_id] = is_applicable


                # 1.5. If the constraint is potentially applicable to the compound,
                # check whether the constraint actually applies.
                if is_applicable:
                    applies = is_applied_func(*args_applies)
                else:
                    applies = None

                pbar.update(1)
                return item, is_applicable, applies
                

            (
                appl_index[c_id + "_item"],
                appl_index[c_id + "_is_applicable"],
                appl_index[c_id + "_applies"]
            ) = zip(*dataset.apply(_measure_constraint, axis=1))

            pbar.close()


            # 2. Calculate statistics

            # 2.1. Type coverage: proportion of the number of compounds for which the
            # constraint is potentially applicable, and the total number of the compounds.

            cvg_type_abs = appl_index[c_id + "_is_applicable"].sum()    # n comps covered

            # there is 1 constraint in this iteration for which no applicable
            # compounds (hence, items) were found in the dataset;
            # might also be the case for further constraints added in the future
            if not cvg_type_abs:
                cvg_type = 0.0
                cvg_item = 0.0
                # regs stay NA
                continue

            cvg_type = cvg_type_abs / N   # n comps covered / n all comps


            # 2.2. Item coverage: proportion of the number of application items for which the
            # constraint is potentially applicable, and the total number of the application items.

            # in this version, we pre-calculate the numbers in data_utils/dataset_stats.ipynb
            Ni = datasets_n_appl_items[dname]

            # for constraints with the application item "compound",
            # item and type measures are effectively the same thing
            if appl_item == "compound":

                cvg_item_abs = copy.copy(cvg_type_abs)
                cvg_item = copy.copy(cvg_type)

            else:

                # since we are talking about potential applicability here, it cannot be
                # True in one compound and False in another compound for the same item;
                # we therefore can remove item duplicates and will get potential applicability
                # booleans for each single item
                appl_index_item = appl_index[[c_id + "_item", c_id + "_is_applicable"]]
                appl_index_item = appl_index_item[~appl_index_item.duplicated(keep="first")]    \
                    .reset_index(drop=True) \
                    .set_index(c_id + "_item")
                cvg_item_abs = appl_index_item[c_id + "_is_applicable"].sum()    # n items covered

                cvg_item = cvg_item_abs / Ni    # n items covered / n all items 


            # 2.3. Type regularity: proportion of the number of compounds to which
            # the constraint applies, and the number of the covered compounds.

            reg_type_abs = appl_index[c_id + "_applies"].sum()  # n conform
            reg_type = reg_type_abs / cvg_type_abs  # n conform / n covered


            #   2.4. Item regularity: average cross-item type regularity.

            # for constraints with the application item "compound",
            # item and type measures are effectively the same thing
            if appl_item == "compound":

                reg_item = copy.copy(reg_type)
                n_violations = cvg_type_abs - reg_type_abs

                print(f"Calculating statistics for {c_id}: done\n") # unify with tqdm below

            else:

                item_regs = []
                # skip compounds built with items not covered by the constraint
                items = appl_index_item[appl_index_item[c_id + "_is_applicable"]].index
                # this loop is the only place where it takes some noticeable
                # time to calculate statistics, so we expand this tqdm desc
                # on the entire measurement;
                for item in tqdm(items, desc=f"Calculating statistics for {c_id}"):
                    # TODO: makes not much sense for l2p constraints because an N1 that takes
                    # the target link is all the same in all bw item compounds
                    bw_item = appl_index[appl_index[c_id + "_item"] == item]    # bw = built with
                    Nbwi = len(bw_item)    # n bw item
                    reg_bw_item_abs = bw_item[c_id + "_applies"].sum()  # n bw item conform
                    reg_bw_item = reg_bw_item_abs / Nbwi # n bw item conform / n bw item covered
                    item_regs.append(reg_bw_item)
                reg_item = pd.array(item_regs).mean().item()   # avg over (n bw item conform / n bw item covered)s
                # calculate n_violations cumulatively:
                # the sum of the violation rate of each compound;
                # for example, if one item always builds deviant compounds,
                # and four items have regularities of 0.2,
                # n_violations will be 1.8 items
                violation_rates = 1 - np.array(item_regs)
                n_violations = violation_rates.sum()
                print()


            # 2.5. Determine the support level of the constraint by the dataset.

            is_productive, is_regular, expected_reg_level, actual_reg_level, support_level = (
                REGULARITY_SCALE.get_support_level(
                    quantifier=quantifier,
                    reg_item=reg_item,
                    cvg_item_abs=cvg_item_abs,
                    n_violations=n_violations
                )
            )


            # record
            appl_statistics.loc[c_id, :] = [
                appl_item,
                Ni,
                quantifier,
                cvg_item_abs,
                cvg_item,
                cvg_type,
                reg_item,
                reg_type,
                n_violations,
                is_productive,
                is_regular,
                expected_reg_level,
                actual_reg_level,
                support_level
            ]

        appl_statistics["n_appl_items"] = appl_statistics["n_appl_items"].astype("Int32")
        float_cols = ["cvg_item", "cvg_type", "reg_item", "reg_type", "n_violations"]
        appl_statistics[float_cols] = appl_statistics[float_cols].astype(float).round(3)
        bool_cols = ["is_productive", "is_regular"]
        appl_statistics[bool_cols] = appl_statistics[bool_cols].astype("boolean[pyarrow]")
        all_appl_statistics[dname] = appl_statistics


        # 3. Save results.

        # individual results
        outdir = os.path.join(resdir, dname)
        os.makedirs(outdir, exist_ok=True)

        appl_index_path = os.path.join(outdir, "appl_index.tsv")
        save_tsv(appl_index, appl_index_path)
        # save zip to push to GitHub (TSV is too large and is ignored)
        zip_name = os.path.splitext(appl_index_path)[0] + ".zip"
        with zipfile.ZipFile(zip_name, "w", compression=zipfile.ZIP_DEFLATED) as z:
            z.write(appl_index_path, os.path.basename(appl_index_path))
        # os.remove(appl_index_path)    # ignored by git

        save_tsv(appl_statistics, os.path.join(outdir, "appl_statistics.tsv"))

    # summarize results
    appl_statistics_summary = pd.concat(all_appl_statistics, names=["dataset"]) \
        .swaplevel(0, 1)    \
        .sort_index()   \
        .loc[constr_ids]    # orig order
    appl_statistics_summary[float_cols] = appl_statistics_summary[float_cols]   \
        .astype(float).round(3)
    
    save_tsv(appl_statistics_summary, os.path.join(resdir, "appl_statistics_summary.tsv"))
    

if __name__ == "__main__":
    main()