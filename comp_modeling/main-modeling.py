import os
import numpy as np
import pandas as pd
from itertools import product
from tqdm import tqdm
import json
from typing import List

from data_utils.load_datasets import load_appl_ind, save_tsv_generic
from comp_modeling.compxconstraints import CompXConstraints
from comp_modeling.metrics import calculate_ldistr, calculate_metrics

rng = np.random.default_rng(579372518)


# python3 -m comp_modeling.main-modeling
def main():

    # When modeling compounding, we have three options as of
    # what to use as the confidence score to resolve constraint
    # conflicts:
    # * Regularity (Albright & Hayes 2002). While Albright & Hayes 2002
    # use type regularity as raw confidence and derive a final confidence
    # out of it by adding the absolute coverage into equation, we do not
    # replicate this step. TODO: add justification. We therefore use
    # item regularity instead.
    # * Specificity (Yang 2016, TODO). In accordance with the Elsewhere Condition,
    # the order of the rule application follows the decrease of generalization
    # specificity, starting with the most specific and finishing with the
    # most general (default) constraint. We define two variants of "specificity":
    # 1. Coverage specificity. Specificity is simply defined by the number
    # of the covered compounds: the more covered compounds, the less
    # specific the constraints.
    # 2. Condition specificity. Specificity of the constraint is defined by the
    # specificity of the linguistic conditions on its potential applicability.
    # This should take into account both the composition of the conditions,
    # and the specificity of each singular condition in its composition.
    # For example, [PL:e] is less specific than [PL:e] & [sem:PL],
    # whereas [coda:VO] is less specific than [coda:e].
    # * While further effects hold (stem frequency, rule frequency, etc.
    # see Yang 2016, we initially concentrate on these two as the baseline.
    #
    # `data_utils/get_constr_confidences.py` calculates these three confidence
    # scores for our constraints. `data_utils/prepare_merged_geco_sp_appl_ind.py`
    # merges the applicability indices obtained from GeCoDB_v07_GN and SP18_Pl_Constr 
    # so that all the constraints implemented so far are defined over the resulting
    # dataset. It counts ~900 compounds that mostly take either a zero linker
    # or a pluralic linker; -s- is underrepresented there. It also mostly consists
    # of simplices which leaves most of the derivational constraints out of sight.
    # These two facts are to be considered as a limitation of this first modeling 
    # attempt. Finally, `comp_modeling/compxconstraints.py` implements the class
    # to predict the linkers from the constraints, followed by each of the three
    # confidence score variants we have.
    # 
    # This script runs the modeling over the ~900 compounds. It records the 
    # resulting linker conflicts, linker rankings, and predictions, and
    # calculates the metrics of the prediction.

    # load the joint applicability index
    appl_ind_path = "resources/developed/merged_geco_sp_appl_ind.tsv"
    appl_ind = load_appl_ind(
        appl_ind_path=appl_ind_path,
        # this dataset is clean
        remove_na_columns=False,
        remove_unconfirmed=False,
        remove_missing=False
    )
    N = len(appl_ind)
    cXc = [
        CompXConstraints(row)
        for _, row in tqdm(appl_ind.iterrows(), total=N, desc="Building X")
    ]
    Y_true = appl_ind["linker"].to_list()


    # record the acceptable and the unacceptable linkers
    # for each compound to be able to inspect the initial
    # conflict before its resolution
    os.makedirs("out", exist_ok=True)

    acceptable_linkers_all = {
        cxc.comp_gecodb: cxc.acceptable_linkers
        for cxc in cXc
    }
    with open("out/acceptable_linkers.json", "w", encoding="utf-8") as o:
        
        json.dump(acceptable_linkers_all, o, ensure_ascii=False, indent=4)
    unacceptable_linkers_all = {
            cxc.comp_gecodb: cxc.unacceptable_linkers
            for cxc in cXc
        }
    with open("out/unacceptable_linkers.json", "w", encoding="utf-8") as o:
        json.dump(unacceptable_linkers_all, o, ensure_ascii=False, indent=4)


    # run available models and record their metrics

    def pred_df(pred_rows: List[pd.DataFrame]) -> pd.DataFrame:
        pred_rows_df = pd.concat(pred_rows, axis=1).T   \
            .reset_index(drop=True) \
            .set_index(appl_ind.index)
        Y_pred = [pred_row.name or "_" for pred_row in pred_rows]
        pred_df = pd.DataFrame(
            {"true": Y_true, "pred": Y_pred},
            index=appl_ind.index
        )
        return pd.concat((pred_df, pred_rows_df), axis=1)

    def record_results(output: dict, outdir: str) -> None:

        # preds
        save_tsv_generic(
            pred_df(output["pred_row"]),
            os.path.join(outdir, "preds.tsv")
        )

        # method best stats
        for m_name, metric in zip(
            ["ldistr_comparison", "f1_acc_df", "confusion_matrix"],
            output["metrics"]
        ):
            save_tsv_generic(
                metric,
                os.path.join(outdir, f"{m_name}.tsv")
            )

        # method outputs; dump to dicts, from which they are
        # nicely recoverable with `pd.DataFrame.from_dict()`
        for key in ["gen_constr_df", "restr_constr_df", "linker_scoreboard"]:
            if not key in output:
                continue
            outdict = {
                # TODO: this changes float precision,
                # e.g. 1.602 becomes 1.6019999999999999;
                # we squeeze the df with `orient="tight"`
                # in order to prevent index collision for
                # multi-linker constraints (they are used
                # as dict keys and collide otherwise)
                comp: df.to_dict(orient="tight")
                for comp, df
                in zip(appl_ind.index, output[key])
            }
            with open(
                os.path.join(outdir, f"{key}s.json"), "w", encoding="utf-8"
            ) as o:
                json.dump(outdict, o, ensure_ascii=False, indent=4)

    metrics = {}
    outputs = {}

    # start with the baselines
    
    # baseline 1: zero linker only
    preds_zero = ["_"] * N
    metrics["zero"] = calculate_metrics(Y_true, preds_zero)

    # baseline 2: random distribution-aware sampling
    ldistr = calculate_ldistr(Y_true)
    preds_rand = rng.choice(
        ldistr.index, size=N, replace=True, p=ldistr
    ).tolist()
    metrics["rand"] = calculate_metrics(Y_true, preds_rand)

    # now proceed to our constraint-based models; in their case,
    # we additionally record the outputs such are 
    # constraint conflicts etc.
    s = lambda x: "+" if x else "-"
    methods = ["albright-hayes", "yang-cvg", "yang-cond"]
    for method in methods:
        
        print(f"\nModeling with the {method} method...")

        outputs[method] = {}
        for count_def, coop, l2p in product([True, False], repeat=3):
            
            # key
            key = f"{s(count_def)}count_def|{s(coop)}coop|{s(l2p)}l2p"

            # placeholders for the outputs
            preds = []
            pred_rows = []
            gen_constr_dfs = []
            if l2p:
                restr_constr_dfs = []
            linker_scoreboards = []

            # prediction
            for cxc in tqdm(cXc, desc=key):
                cxc.predict(
                    method=method,
                    count_def_constr=count_def,
                    constr_cooperation=coop,
                    eliminate_with_l2p=l2p
                )

                # populate the outputs
                preds.append(cxc.y_pred)
                pred_rows.append(cxc.pred_row)
                gen_constr_dfs.append(cxc.gen_constr_df)
                if l2p:
                    restr_constr_dfs.append(cxc.restr_constr_df)
                linker_scoreboards.append(cxc.linker_scoreboard)

            # populate the outputs
            outputs[method][key] = {
                "pred_row": pred_rows,
                "gen_constr_df": gen_constr_dfs,
                "linker_scoreboard": linker_scoreboards
            }
            if l2p:
                outputs[method][key]["restr_constr_df"] = restr_constr_dfs

            # get metrics
            outputs[method][key]["metrics"] = calculate_metrics(Y_true, preds)

        # record the preds, the metrics, and the outputs for each method;
        # since the baselines are trivial, we do not record anything for them
        method_dir = os.path.join("out", method)
        os.makedirs(method_dir, exist_ok=True)

        # method metric summary
        # summarize metrics
        metrics_summary = pd.DataFrame({
            key: {
                "acc": outputs[method][key]["metrics"][1].loc["avg", "acc"],
                "f1": outputs[method][key]["metrics"][1].loc["avg", "f1"]
            }
            for key in outputs[method]
        }).T.sort_values(by=["f1", "acc"], ascending=False)

        # get the best-performing params to record to the overall results
        best_key = metrics_summary["f1"].idxmax()
        best_output = outputs[method][best_key]
        metrics[method] = best_output["metrics"]

        # mark the best key
        metrics_summary["is_best_key"] = False
        metrics_summary.loc[best_key, "is_best_key"] = True

        # now save the metrics summary
        save_tsv_generic(
            metrics_summary,
            os.path.join(method_dir, "metrics_summary.tsv")
        )

        # and record the best results
        record_results(best_output, method_dir)
        
        # and the detailed outputs
        for key, output in outputs[method].items():
            
            kmethod_dir = os.path.join(method_dir, key)
            os.makedirs(kmethod_dir, exist_ok=True)

            record_results(output, kmethod_dir)

    # overall metrics over the two baselines and the three
    # methods at their best parameters
    metric_summary = pd.DataFrame({
        key: {
            "acc": metrics[key][1].loc["avg", "acc"],
            "f1": metrics[key][1].loc["avg", "f1"]
        }
        for key in metrics
    }).T.sort_values(by=["f1", "acc"], ascending=False)

    save_tsv_generic(metric_summary, "out/metrics_summary.tsv")


if __name__ == "__main__":
    main()