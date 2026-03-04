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
                constr_id + "_is_applicable",
                constr_id + "_applies"
            ]
        ]
    )

    constr_statistics = pd.DataFrame(
        index=pd.Series(constr_ids, name="constr_id"),
        columns=[
            "cvg_type",
            "cvg_type_abs",
            "cvg_token",
            "cvg_token_abs",
            "reg_type",
            "reg_type_abs",
            "reg_token",
            "reg_token_abs",
        ]
    )

    type_comp = len(gecodb_v06)
    token_comp = gecodb_v06["comp_freq"].astype(int).sum()

    # For checking the coverage and regularity of constraints,
    # we follow the algorithm:
    # 1. For each compound in GeCoDB for each constraint,
    #   1.1. Check whether the constraint is potentially applicable to the compound.
    #   Cache results for further compounds with the same N1 (most of the constraints
    #   target N1).
    #   1.2. If applicable, check whether the constraint actually applies. Otherwise NA.
    # 2. Calculate statistics:
    #   2.1. Type coverage: proportion of the number of compounds for which the
    #   constraint is potentially applicable and the total number of the compounds.
    #   2.2. Token coverages: proportion of the sums of word counts of the covered compounds
    #   and of all compounds.
    #   2.3. Type regularity: proportion of number of the compounds to which
    #   the constraint applies to the number of the covered compounds
    #   2.4. Token regularity: proportion of the sums of word counts of compounds
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

                # 1.1. Check whether the constraint is applicable.
                is_applicable = is_applicable_func(comp)

                # 1.2. If applicable, check whether the constraint actually applies.
                if is_applicable:
                    applies = is_applied_func(comp)
                else:
                    applies = None

                pbar.update(1)
                return is_applicable, applies
                
            appl_index[c_id + "_is_applicable"], appl_index[c_id + "_applies"] = zip(
                *appl_index.index.to_series().apply(
                    lambda x: _run_constraint(x)
                )
            )

            pbar.close()


            # 2. Calculate statistics

            # 2.1. Type coverage: proportion of the number of compounds for which the
            # constraint is potentially applicable to the total number of the compounds.
            # 2.2. Token coverages: proportion of the sums of word counts of the covered compounds
            # and of all compounds.

            cvg_type_abs = appl_index[c_id + "_is_applicable"].sum()    # n covered
            cvg_type = round(cvg_type_abs / type_comp, 3)   # n covered / n all
            
            applicable_comps = gecodb_v06[appl_index[c_id + "_is_applicable"]]
            cvg_token_abs = applicable_comps["comp_freq"].astype(int).sum()
            cvg_token = round(cvg_token_abs / token_comp, 3)    # freq covered / freq all

            # 2.3. Type regularity: proportion of number of the compounds to which
            # the constraint applies to the number of the covered compounds.
            # 2.4. Token regularity: proportion of the sums of word counts of compounds
            # for which the constraint applies and those for which it is potentially applicable.

            reg_type_abs = appl_index[c_id + "_applies"].sum()  # n conform
            reg_type = round(reg_type_abs / cvg_type_abs, 3)    # n conform / n covered
            
            applied_comps = gecodb_v06[appl_index[c_id + "_applies"].notna() & appl_index[c_id + "_applies"]]
            reg_token_abs = applied_comps["comp_freq"].astype(int).sum()
            reg_token = round(reg_token_abs / cvg_token_abs, 3) # freq conform / freq covered

            constr_statistics.loc[c_id, :] = [
                cvg_type, cvg_type_abs,
                cvg_token, cvg_token_abs,
                reg_type, reg_type_abs,
                reg_token, reg_token_abs
            ]

        else:

            # stays NA
            print(f"Functions for {c_id} not implemented.")


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