# Prerequisites: prepare_celex.py has been run and prepared CELEX data is available.
#                prepare_gecodb.py has been run and prepared GeCoDB data is available.


# TODO merge with check_applicability.py and distinguish by correction_mode=True

import os
import zipfile
import pandas as pd
import yaml
import copy
from tqdm import tqdm

# python -m check_applicability.check_correction_suggestions
from data_utils.gecodb_compound_parser import Compound
from . import applicability_checkers


def main():
    
    gecodb_path = "resources/developed/gecodb_v06.tsv"
    constr_path = "constraints.yaml"
    outdir = "out/applicability_statistics"
    # os.makedirs(outdir, exist_ok=True)

    # load GeCoDB
    gecodb_v06 = pd.read_csv(
        gecodb_path,
        sep="\t",
        dtype=str,
        header=0,
        index_col="comp_gecodb"
    )

    # load constraints and correction suggestions
    with open(constr_path, encoding="utf-8") as f:
        constraints: dict = list(yaml.safe_load_all(f))[-1]["constraints"]

    with open("constraint_corrections.yaml", encoding="utf-8") as f:
        constraint_corrs: dict = list(yaml.safe_load_all(f))[-1]["correction_suggestions"]
        constr_ids = [
            c_id for c_id, constr in constraint_corrs.items()
            if constr["rerun"]
        ]

    # initialize indices; since the operations are symbolic and therefore
    # very fast, we do not create any cache or anything;
    # in case of any changes, the whole thing should be rerun and rebuilt
    # to ensure no outdated infos
    appl_index = pd.DataFrame(
        index=gecodb_v06.index,
        columns=[
            c for constr_id in constr_ids
            for c in [
                constr_id + "_item",    # N1 / N1 + linker / N2 / compound
                constr_id + "_is_applicable",
                constr_id + "_applies"
            ]
        ]
    )

    constr_statistics = pd.DataFrame(
        index=pd.Series(constr_ids, name="constr_id"),
        columns=[
            "n_appl_items",
            "corrected_quantifier",   # for convenience
            "resulting_cvg_item",
            "resulting_cvg_type",
            # "cvg_type_abs",   # can be calculated
            # "cvg_token",      # no meaningful connection type/token was found
            "resulting_reg_item",
            "resulting_reg_type",
            # "reg_type_abs",
            # "reg_token",      # can be found in <outpath>/constr_statistics_legacy.tsv
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
    #   2.1. Type coverage: proportion of the number of compounds for which the
    #   constraint is potentially applicable and the total number of the compounds.
    #   2.2. Item coverage: proportion of the number of items (mostly N1) for which the
    #   constraint is potentially applicable and the total number of the items.
    #   2.3. Type regularity: proportion of number of the compounds to which
    #   the constraint applies to the number of the covered compounds
    #   2.4. Item regularity: the average over the proportions of number of the compounds
    #   to which the constraint applies that are constituted by the covered item to the
    #   total number of compounds that are constituted by the covered item, for each item.
    #   This methodology basically estimates the type regularity within each item (mostly N1)
    #   and then averages these estimates over all covered items. This is done to handle cases
    #   when one very productive N1 deviates from a compound, resulting is a huge disbalance
    #   in type regularity. E.g. in `p2l:drv:deadj_schwa$-0/en`, 555 out of 4214 compounds
    #   were constituted by a single N1 'Liebe' and deviated from the constraint; thus,
    #   even though only one single item was deviating, the type regularity sinked to 0.868.
    #   DISCARDED. Token coverage: proportion of the sums of word counts of the covered compounds
    #   and of all compounds.
    #   DISCARDED. Token regularity: proportion of the sums of word counts of compounds
    #   for which the constraint applies and those for which it is potentially applicable.
    # 3. Save results.

    for c_id, constraint in constraint_corrs.items():

        if not constraint["rerun"]:
            continue
        
        orig_constr = constraints[c_id]
        func_name = orig_constr["func_alias"]

        appl_item = orig_constr["appl_item"]
        
        is_applicable_func = getattr(
            applicability_checkers,
            func_name + "_is_applicable_corr"
        )

        is_applied_func = getattr(
            applicability_checkers,
            func_name + "_applies_corr"
        )

        pbar = tqdm(gecodb_v06.index, desc=f"Rerunning {c_id}")

        def _run_constraint(comp: str, appl_item: str) -> tuple[str, bool, bool]:

            # parse compound
            comp: Compound = Compound(comp)

            # 1.1. Define the application item of the compound.
            # There are a few possibilities:
            #   * N1. This will be the case for the majority of the constraints.
            #   * N1 + linker. This is for the L2P constraints, where
            #   one N1 may or may not attach the target linker in different compounds,
            #   and then only the cases when it does attach it matter; for example,
            #   if we consider compounds `mutter_sprache` and `mutter_+=_zentrum`,
            #   N1 'mutter' will become the application item for
            #   `p2l:decl_cl:pl:#0_uml-0|def-0` but only that case of 'mutter'
            #   that does attach a `_+=_` will be the item of application
            #   for `l2p:0_uml`. This derives directly from the definitions
            #   of these constraints:
            #   "... nouns that build the plural form with a zero ending and umlaut"
            #   vs "... nouns ... that attach a zero linker with umlaut"
            #   * N2. For `p2l:sem:2const_anim/pers-s`.
            #   * The whole compound. This is for the cases when the semantic type
            #   of the whole compounds matters, such as `p2l:sem:comp_type:copula-0`.
            
            # in this iteration, it will always be N1 or N1 + linker
            match appl_item:
                case "n1":
                    item = comp.stems[0].morph
                case "n1+linker":
                    item = comp.stems[0].morph + comp.linkers[0].gecodb
                case "n2":
                    item = comp.stems[1].morph
                case "compound":
                    item = comp.gecodb

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
                lambda x: _run_constraint(x, appl_item)
            )
        )

        pbar.close()


        # 2. Calculate statistics

        #   2.1. Type coverage: proportion of the number of compounds for which the
        #   constraint is potentially applicable and the total number of the compounds.

        cvg_type_abs = appl_index[c_id + "_is_applicable"].sum()    # n comps covered

        # there is 1 constraint in this iteration for which no applicable
        # compounds (hence, items) were found in the dataset;
        # might also be the case for further constraints added in the future
        if cvg_type_abs:

            cvg_type = round(cvg_type_abs / n_comps, 3)   # n comps covered / n all comps

            #   2.2. Item coverage: proportion of the number of items (mostly N1) for which the
            #   constraint is potentially applicable and the total number of the items.

            # for constraints with the application item "compound",
            # item and type measures are effectively the same thing
            if appl_item == "compound":

                cvg_item = copy.copy(cvg_type)
                n_items = copy.copy(n_comps)

            else:
                
                # recalculated in each compound to account for N1 / N1+linker / N2 possibilities
                items = appl_index[c_id + "_item"].unique().tolist()
                n_items = len(items)
                # since we are talking about potential applicability here, it cannot be
                # True in one compound and False in another compound for the same item;
                # we therefore can remove item duplicates and will get potential applicability
                # booleans for each single item
                appl_index_item = appl_index[
                    ~appl_index[[c_id + "_item", c_id + "_is_applicable"]
                ].duplicated(keep="first")]
                cvg_item_abs = appl_index_item[c_id + "_is_applicable"].sum()    # n items covered

                cvg_item = round(cvg_item_abs / n_items, 3) # n items covered / n all items 
            
            #   DISCARDED. Token coverage: proportion of the sums of word counts of the covered compounds
            #   and of all compounds.
            # >>> applicable_comps = gecodb_v06[appl_index[c_id + "_is_applicable"]]
            # >>> cvg_token_abs = applicable_comps["comp_freq"].astype(int).sum()
            # >>> cvg_token = round(cvg_token_abs / token_comp, 3)    # freq covered / freq all


            #   2.3. Type regularity: proportion of number of the compounds to which
            #   the constraint applies to the number of the covered compounds

            reg_type_abs = appl_index[c_id + "_applies"].sum()  # n conform
            reg_type = round(reg_type_abs / cvg_type_abs, 3)    # n conform / n covered


            #   2.4. Item regularity: the average over the proportions of number of the compounds
            #   to which the constraint applies that are constituted by the covered item to the
            #   total number of compounds that are constituted by the covered item, for each item.

            # for constraints with the application item "compound",
            # item and type measures are effectively the same thing
            if appl_item == "compound":

                reg_item = copy.copy(reg_type)
                print(f"Recalculating statistics for {c_id}: done\n") # unify with tqdm below

            else:

                item_regs = []
                # this loop is the only place where it takes some noticeable
                # time to calculate results, so we generalize and use this desc for the whole computation
                for item in tqdm(items, desc=f"Recalculating statistics for {c_id}"):
                    # TODO: optimize (with matrix application?)
                    # skip compounds built with items not covered by the constraint
                    # since we removed duplicates, there will be exactly one record for the item
                    if not appl_index_item[appl_index_item[c_id + "_item"] == item].iloc[0][c_id + "_is_applicable"]:
                        continue
                    # TODO: makes not much sense for l2p constraints because an N1 that takes
                    # the target link is all the same in all bw item compounds
                    bw_item = appl_index[appl_index[c_id + "_item"] == item]    # bw = built with
                    n_bw_item = len(bw_item)    # n bw item
                    reg_bw_item_abs = bw_item[c_id + "_applies"].sum()  # n bw item conform
                    reg_bw_item = round(reg_bw_item_abs / n_bw_item, 3) # n bw item conform / n bw item covered
                    item_regs.append(reg_bw_item)
                reg_item = round(pd.array(item_regs).mean().item(), 3)   # avg over (n bw item conform / n bw item covered)s
                print()

            
            #   DISCARDED. Token regularity: proportion of the sums of word counts of compounds
            #   for which the constraint applies and those for which it is potentially applicable.
            # >>> applied_comps = gecodb_v06[appl_index[c_id + "_applies"].notna() & appl_index[c_id + "_applies"]]
            # >>> reg_token_abs = applied_comps["comp_freq"].astype(int).sum()
            # >>> reg_token = round(reg_token_abs / cvg_token_abs, 3) # freq conform / freq covered

            constr_statistics.loc[c_id, :] = [
                # even though the item variant is calculated
                # after the type variant, we give the prevalence
                # to the former
                n_items,
                constraint["corrected_quantifier"],
                cvg_item, cvg_type,
                reg_item, reg_type
            ]

        else:

            # stays NA
            print(f"No covered items/compounds found for {c_id}.\n")


    # 3. Save results.

    csv_kwargs = {
        "sep": "\t",
        "header": True,
        "index": True
    }

    appl_index_path = os.path.join(outdir, "appl_index_corr.tsv")
    appl_index.to_csv(
        appl_index_path,
        **csv_kwargs
    )
    zip_name = os.path.splitext(appl_index_path)[0] + ".zip"
    with zipfile.ZipFile(zip_name, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.write(appl_index_path, os.path.basename(appl_index_path))
    os.remove(appl_index_path)
        
    constr_statistics.to_csv(
        os.path.join(outdir, "constr_statistics_corr.tsv"),
        **csv_kwargs
    )


if __name__ == "__main__":
    main()