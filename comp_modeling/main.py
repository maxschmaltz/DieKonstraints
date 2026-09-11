import numpy as np
import pandas as pd
from sklearn.metrics import (
    precision_recall_fscore_support,
    accuracy_score, balanced_accuracy_score,
    confusion_matrix
)
from itertools import product, pairwise
from tqdm.notebook import tqdm
from typing import List, Tuple, Optional

from data_utils.load_datasets import load_appl_ind
from comp_modeling.compxconstraints import CompXConstraints

rng = np.random.default_rng(579372518)


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

    # define the metrics
    def calculate_ldistr(linkers: List[str]) -> pd.Series:
        n = len(linkers)
        unique_linkers = np.unique(linkers)
        return pd.Series({
            l: linkers.count(l) / n
            for l in unique_linkers
        }).sort_values(ascending=False)#.round(3)

    ldistr = calculate_ldistr(Y_true)
    def compare_ldistr(linkers: List[str]) -> pd.DataFrame:
        test_ldistr = calculate_ldistr(linkers).to_frame("ours")
        return ldistr.to_frame(name="reference")    \
            .join(test_ldistr)  \
            .fillna(0)  \
            .round(3)

    def calculate_accuracies(Y_pred: List[str]) -> pd.Series:
        eval_df = pd.DataFrame({"true": Y_true, "pred": Y_pred})
        accuracies_data = {}
        for linker in ldistr.index:
            eval_df_linker = eval_df[eval_df["true"] == linker]
            acc = accuracy_score(eval_df_linker["true"], eval_df_linker["pred"])
            accuracies_data[linker] = acc
        accuracies_df = pd.Series(accuracies_data, index=ldistr.index)
        overall_acc = accuracy_score(eval_df["true"], eval_df["pred"])
        balanced_acc = balanced_accuracy_score(eval_df["true"], eval_df["pred"])
        accuracies_df = pd.concat((
            pd.Series({
                "overall": overall_acc,
                "balanced": balanced_acc
            }),
            accuracies_df
        ))
        return accuracies_df.round(3)

    def calculate_f1s(Y_pred: List[str]) -> pd.DataFrame:
        f1_df = pd.DataFrame(
            precision_recall_fscore_support(
                Y_true, Y_pred,
                labels=ldistr.index,
                zero_division=0
            ),
            index=["prec", "recall", "f1", "N"],
            columns=ldistr.index
        )
        f1_df.insert(0, "avg", f1_df.mean(axis=1))
        f1_df = f1_df.T
        return f1_df.round(3)

    def calculate_confusion_matrix(Y_pred: List[str]) -> pd.DataFrame:
        return pd.DataFrame(
            confusion_matrix(
                Y_true, Y_pred,
                labels=ldistr.index,
                normalize="true"
            ),
            index=ldistr.index,
            columns=ldistr.index,
        ).round(3)

    # entrypoint
    def calculate_metrics(
        Y_pred: List[str]
    ) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.DataFrame]:
        ldistr_comparison = compare_ldistr(Y_pred)
        accuracies_df = calculate_accuracies(Y_pred)
        f1_df = calculate_f1s(Y_pred)
        confusion_matrix = calculate_confusion_matrix(Y_pred)
        return ldistr_comparison, accuracies_df, f1_df, confusion_matrix


    # run available models and record their metrics
    Y_pred = {}
    metrics = {}
    outputs = {}


    # start with the baselines
    
    # baseline 1: zero linker only
    method = "zero"
    Y_pred[method] = ["_"] * N
    metrics[method] = calculate_metrics(Y_pred[method])

    # baseline 2: random distribution-aware sampling
    method = "rand"
    Y_pred[method] = rng.choice(
        ldistr.index, size=N, replace=True, p=ldistr
    ).tolist()
    metrics[method] = calculate_metrics(Y_pred[method])

    # now proceed to our constraint-based models; in their case,
    # we additionally record the outputs such are 
    # constraint conflicts etc.
    s = lambda x: "+" if x else "-"
    for method in ["albright-hayes", "yang-cond", "yang-cvg"]:
        
        print(f"\n\nModeling with the {method} method...")

        outputs[method] = {}
        for count_def, coop, l2p in product([True, False], repeat=3):
            
            # key
            key = (f"{s(count_def)}count_def|{s(coop)}coop|{s(l2p)}l2p")

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
                    restrict_with_l2p=l2p
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
                "Y_pred": preds,
                "pred_row": pred_rows,
                "gen_constr_df": gen_constr_dfs,
                "linker_scoreboard": linker_scoreboards
            }
            if l2p:
                outputs[method][key]["restr_constr_df"] = restr_constr_dfs

            # get metrics
            outputs[method][key]["metrics"] = calculate_metrics(preds)

        # summarize metrics
        outputs[method]["metrics_summary"] = pd.DataFrame({
            key: {
                "acc": outputs[method][key]["metrics"][1].loc["overall"],
                "acc_balanced": outputs[method][key]["metrics"][1].loc["balanced"],
                "f1_avg": outputs[method][key]["metrics"][2].loc["avg", "f1"]
            }
            for key in outputs[method]
        }).T.sort_values(by=["f1_avg", "acc_balanced", "acc"], ascending=False)

        # get the best-performing params to record to the overall results
        # and record these results to the overall results
        best_key = outputs[method]["metrics_summary"]["f1_avg"].idxmax()
        Y_pred[method] = outputs[method][best_key]["Y_pred"]
        metrics[method] = outputs[method][best_key]["metrics"]

    # now that we are done with the modeling, we summarize and record the results





if __name__ == "__main__":
    main()