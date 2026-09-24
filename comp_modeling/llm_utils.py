import os
import asyncio
import requests
from typing import List, Optional
import dotenv

dotenv.load_dotenv()


#region DEPRECATED


# Description of the Qwen3.5 9B model:

    # Qwen3.5 9B: open-source small-to-mid-sized (range 4B-9B) multilingual LLM.
    # Seems to offers an optimal quality-cost ratio
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

    ########################################

# Load a HF model locally:

    # download to the local project folder for easier cleanup later
    #     model_dir = os.path.join(_llm_dir, hf_id)
    #     if not os.path.exists(model_dir):
    #         # download the model,
    #         # https://huggingface.co/docs/huggingface_hub/v1.32.0/en/package_reference/file_download#huggingface_hub.snapshot_download
    #         huggingface_hub.snapshot_download(hf_id, local_dir=model_dir)
    
    ########################################

# Run Qwen with Transformers.pipeline (cannot manage thinking):

    #     # adapted from https://huggingface.co/Qwen/Qwen3.5-9B?library=transformers
    #
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
    #     llm = pipeline(
    #         # we need the simplest text generation pipeline,
    #         # https://huggingface.co/docs/transformers/v5.17.0/en/main_classes/pipelines#transformers.TextGenerationPipeline
    #         task="text-generation",
    #         model=model_dir,
    #         # https://docs.pytorch.org/docs/2.14/notes/mps.html
    #         device="mps" if torch.backends.mps.is_available() else "cpu",
    #         generation_config=GenerationConfig(**gen_kwargs)
    #     )
    #     output = llm(text_inputs=messages, **default_gen_kwargs)
    #     response = output[0]["generated_text"].strip()

    ########################################

# Run Qwen with OpenAI completions API (cannot modulate temperature, top_p etc.):

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
    #
    #     # now the model will read the parameters from this json when initialized
    #     device="mps" if torch.backends.mps.is_available() else "cpu"
    #     transformers_bin = os.path.join(_venv_path, "bin", "transformers")
    #     server = subprocess.Popen([
    #         transformers_bin, "serve", model_dir, "--port", str(_port), "--device", device
    #     ])
    #     wait_for_server()
    #
    #     # get the client
    #     client = OpenAI(base_url=_endpoint, api_key="EMPTY")
    #
    #     response = client.chat.completions.create(
    #         model=model_dir,
    #         messages=messages,
    #         extra_body={
    #             "chat_template_kwargs": {
    #                 "enable_thinking": enable_thinking
    #             }
    #         }
    #     )
    #     response.choices[0].message.content

    ########################################

# Run Qwens with vanilla Transformers;
# adapted from https://huggingface.co/Qwen/Qwen3.5-9B/discussions/13, LeonardZhong on Apr 5:

    # tokenizer = AutoTokenizer.from_pretrained(model_id)
    # # https://huggingface.co/docs/transformers/v5.17.0/en/model_doc/auto#transformers.AutoModelForCausalLM.from_pretrained
    # device = "mps" if torch.backends.mps.is_available() else "cpu"
    # llm = AutoModelForCausalLM.from_pretrained(model_dir, device_map=device)
    # model_inputs = tokenizer([text], return_tensors="pt").to(llm.device)
    # generated_ids = llm.generate(**model_inputs, **_gen_kwargs)
    # response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    # raw_answer = response.split("assistant\n")[-1]
    # clean_answer = re.sub(r"<think>.*?</think>", "", raw_answer, flags=re.DOTALL).strip()

    ########################################

# Run GLM-5.3-Flash with NVIDIA:

    # # Hooray NVIDIA again!!!
    # # https://build.nvidia.com/z-ai/glm-5-3-flash
    # client = OpenAI(
    #     base_url = "https://integrate.api.nvidia.com/v1",
    #     api_key = os.environ["NVIDIA_API_KEY"]
    # )

    # return client.chat.completions.create(
    #     model="z-ai/glm-5.3-flash",
    #     messages=messages,
    #     temperature=0.5,
    #     top_p=1,
    #     max_tokens=1024,
    #     stream=False,
    #     reasoning_effort="low"
    # )


#endregion


# GLM-5.3-Flash: the latest model from Z.ai released
# at the end of August 2026 called GLM-5.3-Flash. This is a multilingual
# multimodal 320B model with 18B active parameters.
# 
# The HF model card: https://huggingface.co/zai-org/GLM-5.3-Flash.
# GLM Cloud Console: https://console.gmicloud.ai/user-console/ie/model-hub/llm/60e50c31-b7d0-45a9-b83b-905a0d169c10.
# Technical report: https://arxiv.org/abs/2602.15763.
# 
# At the state of Sep 21, 2026:
#
# This model is the best performing open-source model on the
# German benchmark DACH-bench spanning six evaluation tasks
# on different aspects of NLU: https://dach.peerbench.ai,
# model profile https://dach.peerbench.ai/models/z-ai/glm-5.3-flash,
# being the 8th model overall. It outperforms all QWEN's, all Gemini
# Flash versions until 3.7, and GPT 5.6-Terra.
#
# It is also the best open-source model on a more extensive EuroEval
# benchmark for German including the six DACH-bench but also further
# NLU tasks: https://huggingface.co/spaces/EuroEval/euroeval_leaderboard,
# being the 2nd model overall for German there. It is comparable to
# Gemini-3.7-Flash on this benchmark and is outperformed only by
# GPT-6-Astra.
#
# Most importantly for our use case, this model is the best open-source
# model on the ScaLa dataset: https://dach.peerbench.ai/#tab-scala_de.
# ScaLa-de tests the LLMs for grammatical acceptability of German sentences
# on grammatically correct vs. minimally (!) corrupt German sentences.
# For example, the model correctly marks the sentence 'Ob dieser Satz korrekt ist,
# weißt er nicht.' ungrammatical but '... weiß er nicht.' grammatically correct.
# That indicates that the model possesses a substantial German 
# linguistic competence and is a good candidate to have acquired
# constraints on complex German phenomena.
#
# Its strong general NLU abilities are further confirmed by the fact that 
# in the overall EuroEval competition, it shares the first place with
# GPT-6-Astra, outperforming all Gemini's, QWEN's, DeepSeek's etc.

MODEL_ID = "zai-org/GLM-5.3-Flash"
# https://console.gmicloud.ai/user-console/ie/model-hub/llm/60e50c31-b7d0-45a9-b83b-905a0d169c10
URL = "https://api.gmi-serving.com/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ['GMI_CLOUD_API_KEY']}"
}


def generate_with_llm(
    *,
    messages: List[dict],
    **gen_kwargs
) -> dict:

    # https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create?site_locale=en
    _gen_kwargs = {
        # "max_tokens": 512,
        "max_completion_tokens": 512,
        "temperature": 0.6,
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0,
        "reasoning_effort": "high"  # "low" / "high" / "max"
    }
    _gen_kwargs.update(gen_kwargs)

    payload = {
        "model": MODEL_ID,
        "messages": messages,
        **_gen_kwargs
    }

    try:
        response = requests.post(URL, headers=HEADERS, json=payload, timeout=30)
        return response
    except requests.exceptions.ReadTimeout:
        return


# https://console.gmicloud.ai/user-console/ie/model-hub/llm/60e50c31-b7d0-45a9-b83b-905a0d169c10
async def agenerate_with_llm(
    *,
    messages: List[dict],
    timeout: Optional[int]=15,
    **gen_kwargs
) -> dict:

    _gen_kwargs = {
        # "max_tokens": 512,
        "max_completion_tokens": 512,
        "temperature": 0.6,
        "presence_penalty": 0.0,
        "reasoning_effort": "high"  # "low" / "high" / "max"
    }
    _gen_kwargs.update(gen_kwargs)

    payload = {
        "model": MODEL_ID,
        "messages": messages,
        **_gen_kwargs
    }

    try:
        response = await asyncio.to_thread(
            requests.post,
            URL,
            headers=HEADERS,
            json=payload,
            timeout=timeout
        )
        return response
    except requests.exceptions.ReadTimeout:
        return