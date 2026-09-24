# prerequisites: run main-modeling.py

import os
import asyncio
import requests
import json
from tqdm.asyncio import tqdm_asyncio

from comp_modeling.llm_utils import MODEL_ID, agenerate_with_llm
from comp_modeling.prompts import CLASS_RANKING_PROMPT

MAX_CONCURRENT_REQUESTS = 10


async def classify(ranking, semaphore):

    message = {
        "role": "user",
        "content": CLASS_RANKING_PROMPT.format(
            principle=ranking["principle"]
        )
    }

    # on this task, we do not want the model to reason
    # about its choice, we only want strict classification
    async with semaphore:
        response = await agenerate_with_llm(
            messages=[message],
            max_completion_tokens=512,
            temperature=0.0,
            reasoning_effort="low"
        )

    comp_gecodb = ranking["comp_gecodb"]

    if response is None:
        return {
            "comp_gecodb": comp_gecodb,
            "label": None,
            "response": "Error",
            "reasoning": "Timeout error"
        }

    elif response.status_code == 200:
        response_json = response.json()
        completion = response_json["choices"][0]["message"]
        response = completion["content"].lower().replace("*", "").replace("\"", "")
        label = response if response in ["reg", "cvg", "cond"] else None
        reasoning = completion.get("reasoning_content", "")
        return {
            "comp_gecodb": comp_gecodb,
            "label": label,
            "response": response,
            "reasoning": reasoning
        }

    else:
        try:
            error_body = response.json()
        except requests.exceptions.JSONDecodeError:
            error_body = response.text
        return {
            "comp_gecodb": comp_gecodb,
            "label": None,
            "response": "Error",
            "reasoning": error_body
        }
    

# python3 -m comp_modeling.main-llm-class-rank
async def main():

    # In this script, we employ GLM-3.5-Flash to classify its explanations
    # about the German constraint ranking principles.

    model_id = os.path.split(MODEL_ID)[-1]
    out_dir = os.path.join("out", model_id)
    # os.makedirs(out_dir, exist_ok=True)
    rankings_out_path = os.path.join(out_dir, "constraint_ranking.jsonl")
    with open(rankings_out_path, encoding="utf-8") as r:
        rankings_all = [json.loads(line) for line in r if line.strip()]

    # for logging
    princ_class_path = os.path.join(out_dir, "principle_classification.jsonl")
    # for logging
    if os.path.exists(princ_class_path):
        with open(princ_class_path, encoding="utf-8") as pc:
            classes = [json.loads(line) for line in pc if line.strip()]
        # drop NAs to regenerate them
        classes = [pc for pc in classes if pc["label"] is not None]
        # ... and remove them from the record
        with open(princ_class_path, "w", encoding="utf-8") as pc:
            for classification in classes:
                pc.write(json.dumps(classification, ensure_ascii=False) + "\n")
        index = [c["comp_gecodb"] for c in classes]
        out = open(princ_class_path, "a", encoding="utf-8")
    else:
        index = []
        out = open(princ_class_path, "w", encoding="utf-8")

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    write_lock = asyncio.Lock()

    async def classify_ranking(ranking):
        
        if ranking["comp_gecodb"] in index:
            # predicted at an earlier run
            return

        ranking = await classify(ranking, semaphore)

        # protect shared state / file handle from concurrent writers
        async with write_lock:
            out.write(json.dumps(ranking, ensure_ascii=False) + "\n")

    tasks = [classify_ranking(ranking) for ranking in rankings_all]

    await tqdm_asyncio.gather(
        *tasks,
        desc="Classifying rankings",
        total=len(tasks),
    )

    out.close()


if __name__ == "__main__":
    asyncio.run(main())