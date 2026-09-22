import numpy as np
import pandas as pd
from sklearn.metrics import (
    precision_recall_fscore_support,
    accuracy_score, # balanced_accuracy_score,
    confusion_matrix
)
from typing import List, Tuple


# define the metrics
def calculate_ldistr(linkers: List[str]) -> pd.Series:
    n = len(linkers)
    unique_linkers = np.unique(linkers)
    return pd.Series({
        l: linkers.count(l) / n
        for l in unique_linkers
    }).sort_values(ascending=False)#.round(3)

def compare_ldistr(Y_true: List[str], linkers: List[str]) -> pd.DataFrame:
    ldistr = calculate_ldistr(Y_true)
    test_ldistr = calculate_ldistr(linkers).to_frame("ours")
    return ldistr.to_frame(name="reference")    \
        .join(test_ldistr)  \
        .fillna(0)  \
        .round(3)

def calculate_f1_acc(
    Y_true: List[str], Y_pred: List[str], labels: List[str]
) -> pd.DataFrame:
    
    # f1s
    f1_df = pd.DataFrame(
        precision_recall_fscore_support(
            Y_true, Y_pred,
            labels=labels,
            zero_division=0
        ),
        index=["prec", "recall", "f1", "N"],
        columns=labels
    )
    f1_df.insert(0, "avg", f1_df.mean(axis=1))
    f1_df = f1_df.T

    # accs
    eval_df = pd.DataFrame({"true": Y_true, "pred": Y_pred})
    accuracies_data = {}
    for linker in labels:
        eval_df_linker = eval_df[eval_df["true"] == linker]
        acc = accuracy_score(eval_df_linker["true"], eval_df_linker["pred"])
        accuracies_data[linker] = acc
    overall_acc = accuracy_score(eval_df["true"], eval_df["pred"])
    accuracies_data["avg"] = overall_acc
    accuracies_df = pd.Series(accuracies_data).to_frame("acc")
    
    # # Deprecated: balanced accuracy correlates well with the F1 score
    # # but is less sensitive; it therefore brings no new information for us
    # # because its functions are taken up entirely by the classic accuracy and F1
    # balanced_acc = balanced_accuracy_score(eval_df["true"], eval_df["pred"])

    # merge
    f1_acc_df = pd.concat((f1_df, accuracies_df), axis=1)
    f1_acc_df.loc["avg", "N"] = len(Y_true)   # correct after averaging
    f1_acc_df = f1_acc_df[["acc", "f1", "N", "prec", "recall"]]

    return f1_acc_df.round(3)

def calculate_confusion_matrix(
    Y_true: List[str], Y_pred: List[str], labels: List[str]
) -> pd.DataFrame:
    return pd.DataFrame(
        confusion_matrix(
            Y_true, Y_pred,
            labels=labels,
            normalize="true"
        ),
        index=labels,
        columns=labels
    ).round(3)

# entrypoint
def calculate_metrics(
    Y_true: List[str],
    Y_pred: List[str]
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.DataFrame]:
    ldistr_comparison = compare_ldistr(Y_true, Y_pred)
    f1_acc_df = calculate_f1_acc(Y_true, Y_pred, labels=ldistr_comparison.index)
    confusion_matrix = calculate_confusion_matrix(Y_true, Y_pred, labels=ldistr_comparison.index)
    return ldistr_comparison, f1_acc_df, confusion_matrix