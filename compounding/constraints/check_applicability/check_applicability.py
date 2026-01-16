# Prerequisites: prepare_celex.py has been run and prepared CELEX data is available.
#                prepare_gecodb.py has been run and prepared GeCoDB data is available.


import os
import pandas as pd
import yaml
from tqdm import tqdm

from compounding.constraints.data_utils.gecodb_compound_parser import Compound
import compounding.constraints.check_applicability.applicability_checkers as applicability_checkers


def main():
    
    inpath = "resources/custom/compounding/intermediate_data"
    outpath = "resources/custom/compounding/applicability_statistics"

    # load prepared CELEX nouns
    celex = pd.read_csv(
        os.path.join(inpath, "celex_nouns.tsv"),
        sep="\t",
        dtype=str,
        header=0,
        index_col="lemma"
    )

    # load GecoDB
    gecodb_v06 = pd.read_csv(
        os.path.join(inpath, "gecodb_v06.tsv"),
        sep="\t",
        dtype=str,
        header=0,
        index_col="comp"
    )

    # load constraints
    with open("compounding/constraints/constraints.yaml", encoding="utf-8") as f:
        constraints: dict = list(yaml.safe_load_all(f))[-1]["constraints"]
        constr_ids = list(constraints.keys())

    # load indices as well as statistics if available
    applicability_cache_path = os.path.join(outpath, "applicability_cache.tsv")
    if os.path.exists(applicability_cache_path):
        applicability_cache = pd.read_csv(
            applicability_cache_path,
            sep="\t",
            dtype=str,
            header=0,
            index_col="lemma"
        )
    else:
        applicability_cache = pd.DataFrame(
            index=celex.index,
            columns=constr_ids
        )

    applicability_index_path = os.path.join(outpath, "applicability_index.tsv")
    if os.path.exists(applicability_index_path):
        applicability_index = pd.read_csv(
            applicability_index_path,
            sep="\t",
            dtype=str,
            header=0,
            index_col="comp"
        )
    else:
        applicability_index = pd.DataFrame(
            index=gecodb_v06.index,
            columns=[
                c for constr_id in constr_ids
                for c in [
                    constr_id + "_is_applicable",
                    constr_id + "_applies"
                ]
            ]
        )

    constraints_statistics_path = os.path.join(outpath, "constraints_statistics.tsv")
    if os.path.exists(constraints_statistics_path):
        constraints_statistics = pd.read_csv(
            constraints_statistics_path,
            sep="\t",
            dtype=str,
            header=0,
            index_col="constr_id"
        )
    else:
        constraints_statistics = pd.DataFrame(
            index=pd.Series(constr_ids, name="constr_id"),
            columns=[
                "coverage_comp",
                "coverage_comp_n",
                "coverage_lemma",
                "coverage_lemma_n",
                "regularity_comp",
                "regularity_comp_n"
            ]
        )

    n_comp = len(gecodb_v06)
    

    # For checking the coverage and regularity of constraints,
    # we follow the algorithm:
    # 1. For each compound in GeCoDB for each constraint,
    #   1.1. Check whether the constraint is applicable to its N1. Cache results.
    #   1.2. If applicable, check whether the constraint actually applies.
    # 2. Calculate statistics:
    #   2.1. Coverage for compounds: proportion of compounds for which the constraint is applicable.
    #   2.2. Coverage for lemmas: number of lemmas for which the constraint is applicable.
    #   2.3. Regularity: proportion of compounds for which the constraint applies
    #       among those for which it is applicable.
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

            # # if had been run, skip
            # if applicability_index[c_id + "_is_applicable"].notna().all():
            #     continue

            # reset columns
            applicability_index[c_id + "_is_applicable"] = pd.NA
            applicability_index[c_id + "_applies"] = pd.NA


            pbar = tqdm(gecodb_v06.index, desc=f"Running {c_id}")

            def _run_constraint(comp: str) -> tuple[bool, bool]:

                # parse compound
                comp: Compound = Compound(comp)

                # 1.1. Check whether the constraint is applicable to its N1.

                # check for applicability in cache
                # TODO: p2l:sem:2const_anim/pers-s?
                lemma = comp.stems[0].morph
                cache_entry = applicability_cache.loc[lemma, c_id]
                if pd.isna(cache_entry):
                    is_applicable = is_applicable_func(comp)
                    applicability_cache.loc[lemma, c_id] = is_applicable
                else:
                    is_applicable = cache_entry

                # 1.2. If applicable, check whether the constraint actually applies.

                if is_applicable:
                    applies = is_applied_func(comp)
                else:
                    applies = False

                pbar.update(1)
                return is_applicable, applies
                
            applicability_index[c_id + "_is_applicable"], applicability_index[c_id + "_applies"] = zip(
                *applicability_index.index.to_series().apply(
                    lambda x: _run_constraint(x)
                )
            )

            pbar.close()


            # 2. Calculate statistics

            # 2.1. Coverage for compounds: proportion of compounds for which the constraint is applicable.

            coverage_comp_n = applicability_index[c_id + "_is_applicable"].sum().item()
            coverage_comp = round(coverage_comp_n / n_comp, 4)

            # 2.2. Coverage for lemmas: number of lemmas for which the constraint is applicable.
            
            coverage_lemma_n = applicability_cache[c_id].sum()  # why not .item()?
            # not all of the lemmas may have been checked because
            # not all of them occur as N1 in GeCoDB
            n_lemmas = applicability_cache[c_id].notna().sum().item()
            coverage_lemma = round(coverage_lemma_n / n_lemmas, 4)
            
            # 2.3. Regularity: proportion of compounds for which the constraint applies
            #   among those for which it is applicable.

            # find applicable compounds
            applicable_comps = applicability_index[applicability_index[c_id + "_is_applicable"]]
            n_applicable_comps = len(applicable_comps)
            if n_applicable_comps > 0:
                regularity_comp_n = applicable_comps[c_id + "_applies"].sum().item()
                regularity_comp = round(regularity_comp_n / n_applicable_comps, 4)
            else:
                regularity_comp = "NA"

            # record statistics
            constraints_statistics.loc[c_id, :] = [
                coverage_comp,
                coverage_comp_n,
                coverage_lemma,
                coverage_lemma_n,
                regularity_comp,
                regularity_comp_n
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

    applicability_cache.to_csv(applicability_cache_path, **csv_kwargs)
    applicability_index.to_csv(applicability_index_path, **csv_kwargs)
    constraints_statistics.to_csv(constraints_statistics_path, **csv_kwargs)


if __name__ == "__main__":
    main()