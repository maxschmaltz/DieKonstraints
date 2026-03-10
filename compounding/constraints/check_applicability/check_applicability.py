# Prerequisites: prepare_celex.py has been run and prepared CELEX data is available.
#                prepare_gecodb.py has been run and prepared GeCoDB data is available.


import os
import zipfile
import pandas as pd
import yaml
from tqdm import tqdm

# python -m compounding.constraints.check_applicability.check_applicability
from ..data_utils.gecodb_compound_parser import Compound
from . import applicability_checkers


def main():
    
    inpath = "resources/custom/compounding/intermediate_data"
    outpath = "resources/custom/compounding/applicability_statistics"

    # load GeCoDB
    gecodb_v06 = pd.read_csv(
        os.path.join(inpath, "gecodb_v06.tsv"),
        sep="\t",
        dtype=str,
        header=0,
        index_col="comp_gecodb"
    )

    # load constraints
    with open("compounding/constraints/constraints.yaml", encoding="utf-8") as f:
        constraints: dict = list(yaml.safe_load_all(f))[-1]["constraints"]
        constr_ids = list(constraints.keys())

    # initialize indices; since the operations are symbolic and therefore
    # very fast, we do not create any cache or anything;
    # in case of any changes, the whole thing should be rerun and rebuilt
    # to ensure no outdated infos
    appl_index = pd.DataFrame(
        index=gecodb_v06.index,
        columns=[
            c for constr_id in constr_ids
            for c in [
                constr_id + "_item",    # N1 / [TODO: N2 / compound]
                constr_id + "_is_applicable",
                constr_id + "_applies"
            ]
        ]
    )

    constr_statistics = pd.DataFrame(
        index=pd.Series(constr_ids, name="constr_id"),
        columns=[
            "cvg_type_item",
            "cvg_type_comp",
            # "cvg_type_abs",   # can be calculated
            # "cvg_token",      # no meaningful connection type/token was found
            # "cvg_token_abs",
            "reg_type_item",
            "reg_type_comp",
            # "reg_type_abs",
            # "reg_token",      # can be found in <outpath>/constr_statistics_legacy.tsv
            # "reg_token_abs",
        ]
    )

    n_comps = len(gecodb_v06)

    # For checking the coverage and regularity of constraints,
    # we follow the algorithm:
    # 1. For each compound in GeCoDB for each constraint,
    #   1.1. Define the application item of the compound. This will be N1 in most
    #   of the cases but can also be N2 or the whole compound.
    #   1.2. Check whether the constraint is potentially applicable to the compound.
    #   Cache results for further compounds with the same N1 (most of the constraints
    #   target N1).
    #   1.3. If applicable, check whether the constraint actually applies. Otherwise NA.
    # 2. Calculate statistics:
    #   2.1. Item coverage: proportion of the number of items (mostly N1) for which the
    #   constraint is potentially applicable and the total number of the items.
    #   2.2. Type coverage: proportion of the number of compounds for which the
    #   constraint is potentially applicable and the total number of the compounds.
    #   2.3. Item regularity: the average over the proportions of number of the compounds
    #   to which the constraint applies that are constituted by the covered item to the
    #   total number of compounds that are constituted by the covered item, for each item.
    #   This methodology basically estimates the type regularity within each item (mostly N1)
    #   and then averages these estimates over all covered items. This is done to handle cases
    #   when one very productive N1 deviates from a compound, resulting is a huge disbalance
    #   in type regularity. E.g. in `p2l:drv:deadj_schwa$-0/en`, 555 out of 4214 compounds
    #   were constituted by a single N1 'Liebe' and deviated from the constraint; thus,
    #   even though only one single item was deviating, the type regularity sinked to 0.868.
    #   2.4. Type regularity: proportion of number of the compounds to which
    #   the constraint applies to the number of the covered compounds
    #   DISCARDED. Token coverage: proportion of the sums of word counts of the covered compounds
    #   and of all compounds.
    #   DISCARDED. Token regularity: proportion of the sums of word counts of compounds
    #   for which the constraint applies and those for which it is potentially applicable.
    # 3. Save results.

    for c_id, constraint in constraints.items():
        
        func_name = constraint["func_alias"]

        if hasattr(applicability_checkers, func_name + "_is_applicable"):
            
            is_applicable_func = getattr(
                applicability_checkers,
                func_name + "_is_applicable"
            )

            is_applied_func = getattr(
                applicability_checkers,
                func_name + "_applies"
            )

            pbar = tqdm(gecodb_v06.index, desc=f"Running {c_id}")

            def _run_constraint(comp: str) -> tuple[bool, bool]:

                # parse compound
                comp: Compound = Compound(comp)

                # 1.1. Define the application item of the compound. In this iteration,
                # it will always be the N1.
                # TODO. adjust for N2 or the whole compound
                item = comp.stems[0].morph

                # 1.2. Check whether the constraint is applicable.
                is_applicable = is_applicable_func(comp)

                # 1.3. If applicable, check whether the constraint actually applies.
                if is_applicable:
                    applies = is_applied_func(comp)
                else:
                    applies = None

                pbar.update(1)
                return item, is_applicable, applies
                
            (
                appl_index[c_id + "_item"],
                appl_index[c_id + "_is_applicable"],
                appl_index[c_id + "_applies"]
            ) = zip(
                *appl_index.index.to_series().apply(
                    lambda x: _run_constraint(x)
                )
            )

            pbar.close()


            # 2. Calculate statistics

            #   2.1. Item coverage: proportion of the number of items (mostly N1) for which the
            #   constraint is potentially applicable and the total number of the items.

            # recalculated in each compound to account for N1 / N2 / compound possibilities
            items = appl_index[c_id + "_item"].unique().tolist()
            n_items = len(items)
            # since we are talking about potential applicability here, it cannot be
            # True in one compound and False in another compound with the same item;
            # we therefore can remove item duplicates and will get potential applicability
            # booleans for each single item
            appl_index_item = appl_index[
                ~appl_index[[c_id + "_item", c_id + "_is_applicable"]
            ].duplicated(keep="first")]
            cvg_item_abs = appl_index_item[c_id + "_is_applicable"].sum()    # n items covered

            # there is 1 constraint in this iteration for which no applicable
            # items (hence, compounds) are found in the dataset;
            # might also be the case for further constraints added in the future
            if cvg_item_abs:

                cvg_item = round(cvg_item_abs / n_items, 3) # n items covered / n all items 

                #   2.2. Type coverage: proportion of the number of compounds for which the
                #   constraint is potentially applicable and the total number of the compounds.

                cvg_type_abs = appl_index[c_id + "_is_applicable"].sum()    # n comps covered
                cvg_type = round(cvg_type_abs / n_comps, 3)   # n comps covered / n all comps
                
                #   DISCARDED. Token coverage: proportion of the sums of word counts of the covered compounds
                #   and of all compounds.
                # >>> applicable_comps = gecodb_v06[appl_index[c_id + "_is_applicable"]]
                # >>> cvg_token_abs = applicable_comps["comp_freq"].astype(int).sum()
                # >>> cvg_token = round(cvg_token_abs / token_comp, 3)    # freq covered / freq all


                #   2.3. Item regularity: the average over the proportions of number of the compounds
                #   to which the constraint applies that are constituted by the covered item to the
                #   total number of compounds that are constituted by the covered item, for each item.

                item_regs = []
                # this loop is the only place where it takes some noticeable
                # time to calculate results, so we generalize and use this desc for the whole computation
                for item in tqdm(items, desc=f"Calculating statistics for {c_id}"):
                    # TODO: optimize (with matrix application?)
                    # skip compounds built with items not covered by the constraint
                    # since we removed duplicates, there will be exactly one record for the item
                    if not appl_index_item[appl_index_item[c_id + "_item"] == item].iloc[0][c_id + "_is_applicable"]:
                        continue
                    bw_item = appl_index[appl_index[c_id + "_item"] == item]    # bw = built with
                    n_bw_item = len(bw_item)    # n bw item
                    reg_bw_item_abs = bw_item[c_id + "_applies"].sum()  # n bw item conform
                    reg_bw_item = round(reg_bw_item_abs / n_bw_item, 3) # n bw item conform / n bw item covered
                    item_regs.append(reg_bw_item)
                reg_item = round(pd.array(item_regs).mean().item(), 3)   # avg over (n bw item conform / n bw item covered)s
                print()

                #   2.4. Type regularity: proportion of number of the compounds to which
                #   the constraint applies to the number of the covered compounds

                reg_type_abs = appl_index[c_id + "_applies"].sum()  # n conform
                reg_type = round(reg_type_abs / cvg_type_abs, 3)    # n conform / n covered
                
                #   DISCARDED. Token regularity: proportion of the sums of word counts of compounds
                #   for which the constraint applies and those for which it is potentially applicable.
                # >>> applied_comps = gecodb_v06[appl_index[c_id + "_applies"].notna() & appl_index[c_id + "_applies"]]
                # >>> reg_token_abs = applied_comps["comp_freq"].astype(int).sum()
                # >>> reg_token = round(reg_token_abs / cvg_token_abs, 3) # freq conform / freq covered

                constr_statistics.loc[c_id, :] = [
                    cvg_item, cvg_type,
                    reg_item, reg_type
                ]

        else:

            # stays NA
            print(f"Functions for {c_id} not implemented.\n")


    # 3. Save results.

    csv_kwargs = {
        "sep": "\t",
        "header": True,
        "index": True
    }

    appl_index_path = os.path.join(outpath, "appl_index.tsv")
    appl_index.to_csv(
        appl_index_path,
        **csv_kwargs
    )
    zip_name = os.path.splitext(appl_index_path)[0] + ".zip"
    with zipfile.ZipFile(zip_name, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.write(appl_index_path, os.path.basename(appl_index_path))
    os.remove(appl_index_path)
        
    constr_statistics.to_csv(
        os.path.join(outpath, "constr_statistics.tsv"),
        **csv_kwargs
    )


if __name__ == "__main__":
    main()