import os
import re
import time
import httpx
import subprocess
import torch
from openai import OpenAI
from transformers import AutoModelForCausalLM, AutoTokenizer
import huggingface_hub
from typing import Optional, List


#region DEPRECATED

# Description of the GLM-5.3-Flash model.
# Cannot use due to insufficient computational budget.

    # # For an initial test, we use the latest model from Z.ai released
    # # at the end of August 2026 called GLM-5.3-Flash. This is a multilingual
    # # multimodal 320B model with 18B active parameters.
    # # 
    # # The HF model card: https://huggingface.co/zai-org/GLM-5.3-Flash.
    # # Technical report: https://arxiv.org/abs/2602.15763.
    # # 
    # # At the state of Sep 21, 2026:
    # #
    # # This model is the best performing open-source model on the
    # # German benchmark DACH-bench spanning six evaluation tasks
    # # on different aspects of NLU: https://dach.peerbench.ai,
    # # model profile https://dach.peerbench.ai/models/z-ai/glm-5.3-flash,
    # # being the 8th model overall. It outperforms all QWEN's, all Gemini
    # # Flash versions until 3.7, and GPT 5.6-Terra.
    # #
    # # It is also the best open-source model on a more extensive EuroEval
    # # benchmark for German including the six DACH-bench but also further
    # # NLU tasks: https://huggingface.co/spaces/EuroEval/euroeval_leaderboard,
    # # being the 2nd model overall for German there. It is comparable to
    # # Gemini-3.7-Flash on this benchmark and is outperformed only by
    # # GPT-6-Astra.
    # #
    # # Most importantly for our use case, this model is the best open-source
    # # model on the ScaLa dataset: https://dach.peerbench.ai/#tab-scala_de.
    # # ScaLa-de tests the LLMs for grammatical acceptability of German sentences
    # # on grammatically correct vs. minimally (!) corrupt German sentences.
    # # For example, the model correctly marks the sentence 'Ob dieser Satz korrekt ist,
    # # weißt er nicht.' ungrammatical but '... weiß er nicht.' grammatically correct.
    # # That indicates that the model possesses a substantial German 
    # # linguistic competence and is a good candidate to have acquired
    # # constraints on complex German phenomena.
    # #
    # # Its strong general NLU abilities are further confirmed by the fact that 
    # # in the overall EuroEval competition, it shares the first place with
    # # GPT-6-Astra, outperforming all Gemini's, QWEN's, DeepSeek's etc.
    # GLM_ID = "zai-org/GLM-5.3-Flash"

    ########################################

# Run the models with Transformers.pipeline: cannot manage thinking.

    # def init_llm(hf_id: Optional[str]=QWEN_ID) -> TextGenerationPipeline:
        
    #     # download to the local project folder for easier cleanup later
    #     model_dir = os.path.join(_llm_dir, hf_id)
    #     if not os.path.exists(model_dir):
    #         # download the model,
    #         # https://huggingface.co/docs/huggingface_hub/v1.32.0/en/package_reference/file_download#huggingface_hub.snapshot_download
    #         huggingface_hub.snapshot_download(hf_id, local_dir=model_dir)

    #     # https://huggingface.co/docs/transformers/v5.17.0/en/main_classes/text_generation#transformers.GenerationConfig
    #     # https://huggingface.co/docs/transformers/v5.17.0/en/main_classes/pipelines#transformers.TextGenerationPipeline.__call__
    #     default_gen_kwargs = {
    #         # We want the model to reason moderately about the constraints, for it to be able
    #         # to actually resolve the conflict using some kind of strategy.
    #         # By default, Qwen3.5's operate in a thinking mode so no need to set that parameter
    #         # (https://huggingface.co/Qwen/Qwen3.5-9B#quickstart).
    #         "do_sample": False,
    #         # # not implemented in HF but I assume
    #         # # it is 0.0 by default then (?)
    #         # "presence_penalty": 0.0,
    #         "repetition_penalty": 1.0,
    #         "max_length": 512,
    #         "max_new_tokens": 512,
    #         "return_full_text": False,
    #         # just to suppress a warning, this param is ignored
    #         "clean_up_tokenization_spaces": False
    #     }
            
    #     # adapted from https://huggingface.co/Qwen/Qwen3.5-9B?library=transformers
    #     llm = pipeline(
    #         # we need the simplest text generation pipeline,
    #         # https://huggingface.co/docs/transformers/v5.17.0/en/main_classes/pipelines#transformers.TextGenerationPipeline
    #         task="text-generation",
    #         model=model_dir,
    #         # https://docs.pytorch.org/docs/2.14/notes/mps.html
    #         device="mps" if torch.backends.mps.is_available() else "cpu",
    #         generation_config=GenerationConfig(**default_gen_kwargs)
    #     )

    #     return llm

    # def generate_with_llm(llm: TextGenerationPipeline, *, messages: list, **gen_kwargs):

    #     # Following the best practices https://huggingface.co/Qwen/Qwen3.5-9B#best-practices,
    #     # we set the parameters for precise coding tasks;
    #     # this ought to counterbalance the creativity with precision.
    #     default_gen_kwargs = {
    #         "temperature": 0.6,
    #         "top_p": 0.95,
    #         "top_k": 20,
    #         "min_p": 0.0
    #     }
    #     default_gen_kwargs.update(gen_kwargs)
        
    #     output = llm(text_inputs=messages, **default_gen_kwargs)
    #     response = output[0]["generated_text"].strip()

    #     return response

    ########################################

# Run the model with OpenAI completions API: cannot modulate
# temperature, top_p etc.

    # _venv_path = ".venv"
    # _port = 8000
    # _endpoint = f"http://localhost:{_port}/v1"

    # def wait_for_server(timeout=90):
    #     start = time.time()
    #     while time.time() - start < timeout:
    #         try:
    #             r = httpx.get(f"{_endpoint}/models", timeout=2)
    #             if r.status_code == 200:
    #                 return True
    #         except httpx.RequestError:
    #             pass
    #         time.sleep(3)
    #     raise TimeoutError("Server did not start in time")


    # # adapted from https://huggingface.co/Qwen/Qwen3.5-9B#text-only-input
    # def init_llm(
    #     model: Optional[str]=QWEN_ID,
    #     enable_thinking: Optional[bool]=True,
    #     **gen_kwargs
    # ) -> tuple:
        
    #     # download to the local project folder for easier cleanup later
    #     model_dir = os.path.join(_llm_dir, model)
    #     if not os.path.exists(model_dir):
    #         # download the model,
    #         # https://huggingface.co/docs/huggingface_hub/v1.32.0/en/package_reference/file_download#huggingface_hub.snapshot_download
    #         huggingface_hub.snapshot_download(model, local_dir=model_dir)

    #     # Serve the model. Idk why but Qwen's and Mistral's do not allow
    #     # to manage thinking when called with Transformers but when called 
    #     # with OpenAI completions API, it ignores temperature etc.
    #     # To address that, we will write the sampling parameters directly to
    #     # generation_config.json and will pass the enable_thinking part
    #     # to the completion.
    #     # https://developers.openai.com/api/reference/python/resources/chat/subresources/completions/methods/create
    #     default_gen_kwargs = {
    #         "max_tokens": 20,
    #         # Following the best practices https://huggingface.co/Qwen/Qwen3.5-9B#best-practices,
    #         # we set the parameters for precise coding tasks;
    #         # this ought to counterbalance the creativity with precision.
    #         "temperature": 0.6,
    #         "top_p": 0.95,
    #         "presence_penalty": 0.0,
    #         # "extra_body": {
    #         #     # "repetition_penalty": 1.0,
    #         #     # "top_k": 20,
    #         #     # "min_p": 0.0,
    #         #     "chat_template_kwargs": {"enable_thinking": enable_thinking}
    #         # }
    #     }
    #     default_gen_kwargs.update(gen_kwargs)
    #     # with open(os.path.join(model_dir, "generation_config.json"), "w") as g:
    #     #     json.dump(default_gen_kwargs, g, indent=4)

    #     # now the model will read the parameters from this json when initialized
    #     device="mps" if torch.backends.mps.is_available() else "cpu"
    #     transformers_bin = os.path.join(_venv_path, "bin", "transformers")
    #     server = subprocess.Popen([
    #         transformers_bin, "serve", model_dir, "--port", str(_port), "--device", device
    #     ])
    #     wait_for_server()

    #     # get the client
    #     client = OpenAI(base_url=_endpoint, api_key="EMPTY")

    #     return server, client, model_dir, model

    # def generate_with_llm(
    #     client: OpenAI,
    #     model_dir: str,
    #     *,
    #     messages: list,
    #     enable_thinking: bool
    # ) -> str:

    #     response = client.chat.completions.create(
    #         model=model_dir,
    #         messages=messages,
    #         extra_body={
    #             "chat_template_kwargs": {
    #                 "enable_thinking": enable_thinking
    #             }
    #         }
    #     )

    #     return response.choices[0].message.content

#endregion

#################################################################

# For an initial test, we want an open-source small-to-mid-sized (range 4B-9B)
# multilingual LLM. The LLM should be able to reason and/or follow instructions.
# Qwen3.5 9B satisfies all these criteria and offers an optimal quality-cost ratio
# of all mid-sized LLMs as tested on German NLU benchmarks.
# 
# The HF model card: https://huggingface.co/Qwen/Qwen3.5-9B.
# Technical report: https://qwen.ai/blog?id=qwen3.5.
# 
# At the state of Sep 21, 2026:
#
# Its performance over the German benchmark 
# DACH-bench (https://dach.peerbench.ai) spanning six evaluation
# tasks on different aspects of NLU is as follows
# (https://dach.peerbench.ai/models/qwen/qwen3.5-9b):
# * 35th overall model;
# * 20th open-source model;
# * 2nd (open-source) model in the 4B-20B.
# More detailed comparison of the three best mid-sized
# models on DACH-bench:
# https://dach.peerbench.ai/compare?models=qwen%2Fqwen3.5-9b,qwen%2Fqwen3-14b,google%2Fgemma-4-12b-it.
#
# From the tasks of DACH-bench, we are most interested in the ScaLa-de task
# (https://euroeval.com/tasks/linguistic-acceptability).
# ScaLa-de tests the LLMs for grammatical acceptability of German sentences
# on grammatically correct vs. minimally (!) corrupt German sentences.
# Qwen3.5 9B is the third best (open-source) model on ScaLa:
# https://dach.peerbench.ai/#tab-scala_de, 
# https://dach.peerbench.ai/runs/qwen3-5-9b--scala-de--2026-06-10--1dq2m8w.
# # That indicates that the model possesses at least minimal German 
# linguistic competence and might have acquired constraints on complex German phenomena.
# The reason we do not choose the better Qwen3.5 14B or Gemma 4 12B is that their 
# response latencies are ~15s and ~27s, respectively, while Qwen3.5 9B has 
# an attractive latency of <1s. For such acceleration, we sacrifice a 
# minimal loss in performance relative to these two.
# 
# Qwen3.5 9B also performs 11th on the German split of EuroEval including
# the six DACH-bench but also further NLU tasks
# (https://huggingface.co/spaces/EuroEval/euroeval_leaderboard).
# All better open-source mid-sized models on German EuroEval are
# two Mistral's which are not fine-tuned for reasoning or instructions,
# two Gemma's which are too slow, and some model called Bielik-11B-v3.0-Instruct 
# which I am just not too familiar with.
QWEN_ID = "Qwen/Qwen3.5-9B"
_llm_dir = ".hf_llms"


# adapted from https://huggingface.co/Qwen/Qwen3.5-9B/discussions/13, LeonardZhong on Apr 5
def init_llm(model_id: Optional[str]=QWEN_ID) -> tuple:

    # download to the local project folder for easier cleanup later
    model_dir = os.path.join(_llm_dir, model_id)
    if not os.path.exists(model_dir):
        # download the model,
        # https://huggingface.co/docs/huggingface_hub/v1.32.0/en/package_reference/file_download#huggingface_hub.snapshot_download
        huggingface_hub.snapshot_download(model_id, local_dir=model_dir)
    
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    # https://huggingface.co/docs/transformers/v5.17.0/en/model_doc/auto#transformers.AutoModelForCausalLM.from_pretrained
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    llm = AutoModelForCausalLM.from_pretrained(model_dir, device_map=device)

    return llm, tokenizer, model_id


def generate_with_llm(
    llm: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    *,
    messages: List[dict],
    enable_thinking: bool,
    **gen_kwargs
) -> str:

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        # Most important here!!! While this switch does not turn off the
        # thinking at its whole (as it is possible) with OpenAI completions API,
        # the generations returned when this flag is set to `False`
        # just have an empty thinking process. This approach is then
        # the least evil compared to pipeline which does not allow
        # to disable thinking at all, and OpenAI completions API which
        # does not allow to set `do_sample` to `True`.
        enable_thinking=enable_thinking,
        add_generation_prompt=True
    )

    # https://huggingface.co/docs/transformers/v5.17.0/en/main_classes/text_generation#transformers.GenerationConfig
    _gen_kwargs = {
        # "max_length": 512,
        "max_new_tokens": 512,
        "max_time": 7, # 7s per generation
        # # just to suppress a warning, this param is ignored
        # "clean_up_tokenization_spaces": False
        # Following the best practices https://huggingface.co/Qwen/Qwen3.5-9B#best-practices,
        # we set the parameters for precise coding tasks;
        # this ought to counterbalance the creativity with precision.
        "do_sample": True,
        "temperature": 0.6,
        "top_p": 0.95,
        "top_k": 20,
        "min_p": 0.0,
        # # not implemented with transformers
        # "presence_penalty": 0.0,
        "repetition_penalty": 1.0
    }
    _gen_kwargs.update(gen_kwargs)

    model_inputs = tokenizer([text], return_tensors="pt").to(llm.device)
    generated_ids = llm.generate(
        **model_inputs,
        **_gen_kwargs
    )
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    raw_answer = response.split("assistant\n")[-1]
    clean_answer = re.sub(r"<think>.*?</think>", "", raw_answer, flags=re.DOTALL).strip()
    return clean_answer