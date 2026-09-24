# prerequisites: run main-modeling.py

import os
import random
import asyncio
import requests
import json
from tqdm.asyncio import tqdm_asyncio

from data_utils.load_datasets import load_appl_ind, load_tsv_generic, save_tsv_generic
from data_utils.gecodb_compound_parser import Compound
from comp_modeling.llm_utils import MODEL_ID, agenerate_with_llm
from comp_modeling.prompts import PREDICT_LINKER_PROMPT
from comp_modeling.metrics import calculate_metrics

MAX_CONCURRENT_REQUESTS = 10


async def predict_linker(comp_gecodb, row, acceptable_linkers_all, semaphore):

    acceptable_linkers = list(acceptable_linkers_all[comp_gecodb].keys())
    if len(acceptable_linkers) < 2:
        return None

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
    async with semaphore:
        response = await agenerate_with_llm(
            messages=[message],
            max_completion_tokens=512,
            # ~greedy decoding
            temperature=0,
            reasoning_effort="low"
        )

    if response is None:
        return {
            "comp_gecodb": comp_gecodb,
            "true": row["linker"],
            "pred": "Error",
            "response": "Timeout error",
            "reasoning": "",
        }

    elif response.status_code == 200:
        response_json = response.json()
        completion = response_json["choices"][0]["message"]
        response = completion["content"]
        pred = options.get(response.lower(), "na")
        reasoning = completion.get("reasoning_content", "")
        return {
            "comp_gecodb": comp_gecodb,
            "true": row["linker"],
            "pred": pred,
            "response": response,
            "reasoning": reasoning,
        }

    else:
        try:
            error_body = response.json()
        except requests.exceptions.JSONDecodeError:
            error_body = response.text
        return {
            "comp_gecodb": comp_gecodb,
            "true": row["linker"],
            "pred": "Error",
            "response": error_body,
            "reasoning": "",
        }
    

# python3 -m comp_modeling.main-llm
async def main():

    # In this script, we evaluate GLM-3.5-Flash on our German
    # compounding modeling dataset to estimate its overall
    # knowledge of German compounds, and then proceed to
    # constraint conflict resolution with the model.

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

    model_id = os.path.split(MODEL_ID)[-1]
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
        out.write("comp_gecodb\ttrue\tpred\tresponse\treasoning\n")

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    write_lock = asyncio.Lock()

    async def process_row(comp_gecodb, row):
        
        if comp_gecodb in index:
            # predicted at an earlier run
            return

        result = await predict_linker(
            comp_gecodb, row, acceptable_linkers_all, semaphore
        )

        if result is None:
            # no conflict
            return

        # protect shared state / file handle from concurrent writers
        async with write_lock:
            Y_true.append(result["true"])
            preds.append(result["pred"])
            index.append(result["comp_gecodb"])
            out.write(
                f"{result["comp_gecodb"]}\t{result["true"]}\t{result["pred"]}\t"
                f"{result["response"]}\t{result["reasoning"]}\n"
            )

    tasks = [
        process_row(comp_gecodb, row)
        for comp_gecodb, row in appl_ind.iterrows()
    ]

    await tqdm_asyncio.gather(
        *tasks,
        desc="Predicting compound linkers",
        total=len(tasks),
    )

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
    asyncio.run(main())