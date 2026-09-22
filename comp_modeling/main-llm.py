# prerequisites: run main-modeling.py

import os
import random
import pandas as pd
from tqdm import tqdm
import json

from data_utils.load_datasets import load_appl_ind, load_tsv_generic, save_tsv_generic
from data_utils.gecodb_compound_parser import Compound
from comp_modeling.llm_utils import init_llm, generate_with_llm
from comp_modeling.prompts import PREDICT_LINKER_PROMPT
from comp_modeling.metrics import calculate_metrics


# python3 -m comp_modeling.main-llm
def main():

    # In this script, we evaluate Qwen3.5 9B on our German
    # compounding modeling dataset to estimate its overall
    # knowledge of German compounds, and then proceed to 
    # constraint conflict resolution with the model.

    llm, tokenizer, model_id = init_llm()

    # 1. Evaluate the model for its general knowledge of
    # German compounds.

    appl_ind_path = "resources/developed/merged_geco_sp_appl_ind.tsv"

    appl_ind = load_appl_ind(
        appl_ind_path=appl_ind_path,
        # this dataset is clean
        remove_na_columns=False,
        remove_unconfirmed=False,
        remove_missing=False
    )

    with open("out/acceptable_linkers.json", encoding="utf-8") as i:
        acceptable_linkers_all = json.load(i)

    benchmark_dir = os.path.join("out", model_id, "linker_benchmark")
    os.makedirs(benchmark_dir, exist_ok=True)
    preds_tsv_path = os.path.join(benchmark_dir, "preds.tsv")
    # for logging
    if os.path.exists(preds_tsv_path):
        preds_df = load_tsv_generic(preds_tsv_path)
        # drop NAs...
        preds_df = preds_df[preds_df["pred"] != "na"]
        # and remove them from log
        save_tsv_generic(preds_df.sort_index(), preds_tsv_path)
        Y_true = preds_df["true"].tolist()
        preds = preds_df["pred"].tolist()
        index = preds_df.index.tolist()
        out = open(preds_tsv_path, "a", encoding="utf-8")
    else:
        Y_true = []
        preds = []
        index = []
        out = open(preds_tsv_path, "w", encoding="utf-8")
        out.write("comp_gecodb\ttrue\tpred\tresponse\n")


    for comp_gecodb, row in tqdm(
        appl_ind.iterrows(),
        desc="Predicting compound linkers",
        total=len(appl_ind)
    ):

        if comp_gecodb in index:
            # predicted at ann earlier run;
            # since we predict greedily, the answers are determined
            continue

        acceptable_linkers = list(
            acceptable_linkers_all[comp_gecodb].keys()
        )
        if len(acceptable_linkers) < 2:
            continue

        split = comp_gecodb.split("_")
        n1, n2 = split[0], split[-1]
        options = {}
        for linker in acceptable_linkers:
            if linker.startswith("_+e") and n1.endswith("e"):
                # bring back the en/n allomorphy
                _linker = linker.replace("_+e", "_+")
            else:
                _linker = linker
            option_gecodb = f"{n1}{_linker}{n2}"
            option_lemma = Compound(option_gecodb).lemma
            # to decode LLMs predictions later
            options[option_lemma.lower()] = linker

        # shuffle options in order to eliminate possible order effects
        options_strs = [f"'{option}'" for option in options.keys()]
        random.shuffle(options_strs)
        options_str = ", ".join(options_strs)
        message = {
            "role": "user",
            "content": PREDICT_LINKER_PROMPT.format(
                n1=n1,
                n2=n2,
                variants=options_str
            )
        }
        # on this task, we want to assess models
        # "brute force" knowledge so we turn off
        # thinking and sampling
        response = generate_with_llm(
            llm,
            tokenizer,
            messages=[message],
            enable_thinking=False,
            max_new_tokens=10,  # only pred
            # greedy decoding
            do_sample=False
        ).lower()
        pred = options.get(response, "na")

        # for metrics
        Y_true.append(row["linker"])
        preds.append(pred)
        index.append(comp_gecodb)

        # log
        out.write(f"{comp_gecodb}\t{row["linker"]}\t{pred}\t{response}\n")

    out.close()

    # metrics
    for m_name, metric in zip(
        ["ldistr_comparison", "f1_acc_df", "confusion_matrix"],
        calculate_metrics(Y_true, preds)
    ):
        save_tsv_generic(
            metric,
            os.path.join(benchmark_dir, f"{m_name}.tsv")
        )


if __name__ == "__main__":
    main()