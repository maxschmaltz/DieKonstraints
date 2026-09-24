# prerequisites: run main-modeling.py

import os
import random
import asyncio
import requests
import json
from tqdm.asyncio import tqdm_asyncio

from data_utils.load_datasets import load_tsv_generic, load_constraints
from comp_modeling.llm_utils import MODEL_ID, agenerate_with_llm
from comp_modeling.prompts import format_instructions, RANK_CONSTRAINTS_PROMPT

MAX_CONCURRENT_REQUESTS = 10


async def rank_constraints(comp_gecodb, acceptable_linkers_all, constraints, semaphore):

    conflict = set()
    applicable_c_ids = list(acceptable_linkers_all[comp_gecodb].values())
    for c_ids in applicable_c_ids:
        conflict.update(c_ids)

    conflict = list(conflict)
    # shuffle options in order to eliminate possible order effects
    random.shuffle(conflict)
    conflict_map = {i + 1: c_id for i, c_id in enumerate(conflict)}

    constrs_strs = [
        f"{i + 1}. {constraints[c_id]["summary"]}"
        for i, c_id in enumerate(conflict)
    ]
    constrs_str = "/n".join(constrs_strs)
    message = {
        "role": "user",
        "content": RANK_CONSTRAINTS_PROMPT.format(
            constraints_str=constrs_str
        )
    }
    # https://docs.z.ai/guides/capabilities/struct-output
    messages = [format_instructions, message]

    # on this task, we want the model to reason
    # about its choice; on the other hand, we want
    # a clean response without recycling the same though
    async with semaphore:
        response = await agenerate_with_llm(
            messages=messages,
            max_completion_tokens=4096,
            # don't let recycle the same thought
            frequency_penalty=1.0,
            timeout=45
        )

    if response is None:
        return {
            "comp_gecodb": comp_gecodb,
            "ranking": None,
            "principle": "Error",
            "guess": "",
            "reasoning": "Timeout error"
        }

    elif response.status_code == 200:
        response_json = response.json()
        completion = response_json["choices"][0]["message"]
        response = completion["content"]
        response = response.replace("json", "").replace("`", "")
        reasoning = completion.get("reasoning_content", "")
        try:
            response = json.loads(response)
            ranking = [
                conflict_map.get(i, "NA")
                for i in response["ranking"]
            ]
            return {
                "comp_gecodb": comp_gecodb,
                "ranking": ranking,
                "principle": response["principle"],
                "guess": response["guess"],
                "reasoning": reasoning,
            }
        except:# json.JSONDecodeError:
            return {
                "comp_gecodb": comp_gecodb,
                "ranking": None,
                "principle": response,
                # to recreate the answer manually
                "guess": conflict,
                "reasoning": reasoning,
            }

    else:
        try:
            error_body = response.json()
        except requests.exceptions.JSONDecodeError:
            error_body = response.text
        return {
            "comp_gecodb": comp_gecodb,
            "ranking": None,
            "principle": "Error",
            "guess": "",
            "reasoning": error_body
        }
    

# python3 -m comp_modeling.main-llm-experiment
async def main():

    # In this script, we employ GLM-3.5-Flash to rank constraints
    # in the actual constraint conflicts we encounter during modeling.

    comps_for_modeling_path = "out/comps_for_modeling.tsv"
    X = load_tsv_generic(comps_for_modeling_path)

    with open("out/acceptable_linkers.json", encoding="utf-8") as i:
        acceptable_linkers_all = json.load(i)

    constr_path = "constraints/constraints_all_revised.yaml"
    constraints = load_constraints(constr_path)

    model_id = os.path.split(MODEL_ID)[-1]
    out_dir = os.path.join("out", model_id)
    # os.makedirs(out_dir, exist_ok=True)
    rankings_out_path = os.path.join(out_dir, "constraint_ranking.jsonl")
    # for logging
    if os.path.exists(rankings_out_path):
        with open(rankings_out_path, encoding="utf-8") as r:
            rankings_all = [json.loads(line) for line in r if line.strip()]
        # drop NAs to regenerate them
        rankings_all = [r for r in rankings_all if r["ranking"] is not None]
        # ... and remove them from the record
        with open(rankings_out_path, "w", encoding="utf-8") as r:
            for ranking in rankings_all:
                r.write(json.dumps(ranking, ensure_ascii=False) + "\n")
        index = [r["comp_gecodb"] for r in rankings_all]
        out = open(rankings_out_path, "a", encoding="utf-8")
    else:
        index = []
        out = open(rankings_out_path, "w", encoding="utf-8")

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    write_lock = asyncio.Lock()

    async def process_comp(comp_gecodb):
        
        if comp_gecodb in index:
            # predicted at an earlier run
            return

        ranking = await rank_constraints(
            comp_gecodb, acceptable_linkers_all, constraints, semaphore
        )

        # protect shared state / file handle from concurrent writers
        async with write_lock:
            out.write(json.dumps(ranking, ensure_ascii=False) + "\n")

    tasks = [process_comp(comp_gecodb) for comp_gecodb in X.index]

    await tqdm_asyncio.gather(
        *tasks,
        desc="Ranking constraints",
        total=len(tasks),
    )

    out.close()


if __name__ == "__main__":
    asyncio.run(main())