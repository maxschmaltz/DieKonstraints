# Constraint Conflict Resolution in Neural Language Models: German Nominal Compounding

> August 2026 - September 2026

Initial compounding modeling attempt. Presented in a talk at the [UNC-Tübingen Workshop 2026](https://linguistics.unc.edu/event/learning-and-using-linguistic-structure-computational-and-experimental-perspectives-workshop/).


## Abstract

Recent work suggests that neural language models (LMs) can acquire linguistic generalizations without explicit instruction, but it remains unclear whether they can capture irregular patterns governed by multiple defeasible constraints. Our project, “The Status of Linguistic Constraints in Neural Language Models,” investigates this question through German nominal compounding (GNC), where linking elements are frequent but often difficult to predict even among phonologically, morphologically, and semantically similar nouns. We first introduce the relevant constraint subset and report results from a large-scale corpus study showing that most constraints are violated to varying degrees, with semantically defined constraints being especially irregular. We then turn to modeling constraint conflict resolution with iterative rule-based models and an LM. We report that ranking the constraints by specificity produces the most accurate results, and that the LM intentionally reproduces this ranking approach. We conclude by considering what LM performance on this task can reveal about the representation and interaction of non-categorical linguistic constraints.

## Abstract (Extended)

Recent linguistic studies provide evidence that neural language models (LMs) are capable of capturing linguistic rules without being explicitly trained for it. For instance, Wei et al. (2021) demonstrate that LMs successfully acquire English verb-subject number agreement. Within our long-term project “The Status of Linguistic Constraints in Neural Language Models”, we want to assess to what extent these abstraction capabilities extend to non-regular linguistic generalizations.

We focus on linguistic phenomena governed not by rules but by a set of weak (defeasible) linguistic constraints — that is, linguistic mechanisms and patterns that are subject to repeated violations in the language. Such constraints are often in a conflict when applied to the same input, and the violations arise as a result of favoring one constraint over the others. Whether LMs capture the complex constraint interplay and can model constraint conflict resolution is the key question we address within our long-term project.

This talk will be dedicated to the first phenomenon that we investigate through the lens of constraint interaction — German nominal compounding (GNC). As opposed to English, German eagerly solidifies compounds orthographically, thus creating new lexical entries. Besides, about 40% of German compounds insert a so-called linking element that is not confidently predictable for most of constituent classes. For example, nouns Birne ‘pear’ and Kirsche ‘cherry’ build compounds Birne-n-saft ‘pear juice’ but Kirsch-0-saft ‘cherry juice’ despite having nearly identical phonological, morphological, and semantic properties. GNC is thus a suitable phenomenon for investigating constraint abstraction within LMs.

During the talk, we will first briefly introduce the GNC constraint set and showcase their interaction on German material. We will then discuss the results of our recent large-scale corpus study on GNC. We find that most of the constraints are irregular to a different extent, meaning that they are violated by a considerable share of the items to which they are potentially applicable (application items). We report that constraint regularity decreases drastically in constraints defined over semantic properties (as opposed to morphological, phonological, etc. properties), reaching statistical significance at sig=0.05. We will then move to modeling constraint conflict resolution with iterative rule-based models and an LM. We report that ranking the constraints by specificity produces the most accurate results, and that the LM intentionally reproduces this ranking approach. We will conclude the talk by a brief general discussion of the implications of constraint conflict resolution by LMs in a broader context, and will outline some directions for future research.


## Code Structure

### Constraints

* For the scientific sources from which the original constrain definitions were collected, refer to [Shmalts 2026](https://github.com/maxschmaltz/DieKonstraints/tree/comp_constr_corp_study_mar26) and [Shmalts in preparation](https://github.com/maxschmaltz/DieKonstraints/tree/TODO).

* The summarized and classified constraints are to be found in [constraints/constraints_all_revised.yaml](constraints/constraints_all_revised.yaml). This YAML has a dedicated README inside, refer to it for the structure and the adopted notation of this file. Note that this constraint list has undergone some changes in course of this study; the changes are also described in the YAML README.

* The three confidence variants for each constraint (regularity, coverage score, and specificity score) are stored in [constraints/constr_confidences.tsv](constraints/constr_confidences.tsv). The confidences were collected in [data_utils/get_constr_confidences.py](data_utils/get_constr_confidences.py).


### Data

* The central datasets we used are the constraint applicability indices originated from [Shmalts 2026](https://github.com/maxschmaltz/DieKonstraints/tree/comp_constr_corp_study_mar26) and [Shmalts in preparation](https://github.com/maxschmaltz/DieKonstraints/tree/TODO). For each of the compound they are defined over, these indices record whether a given constraint is potentially and actually applicable to it or not. The applicability indices can be found in the [resources/semrel_comp_corp_study-private/appl_inds](resources/semrel_comp_corp_study-private/appl_inds) directory.

* For the experiments, we merged the two applicability indices in [data_utils/prepare_merged_geco_sp_appl_ind.py](data_utils/prepare_merged_geco_sp_appl_ind.py) by intersecting the compounds they are defined over. The merged applicability index is stored in [resources/developed/merged_geco_sp_appl_ind.tsv](resources/developed/merged_geco_sp_appl_ind.tsv).

* During the experiments, we referred to several datasets to define the potential applicability of restrictive (L2P) constraints to input compounds. These are [CELEX-nouns](resources/semrel_comp_corp_study-private/celex_nouns.tsv) derived from CELEX2 in Shmalts 2026, GeCoDB_v07_GN derived from Shmalts 2026 GeCoDB_v06 in Shmalts in preparation, and [GermaNet](resources/GermaNet). CELEX-nouns and GermaNet are unavailable in the public version due to the copyright restrictions.


### Experiments & Tests

* The code for parsing compounds (in GeCoDB_vXX notation) is available in [data_utils/gecodb_compound_parser.py](data_utils/gecodb_compound_parser.py), and the corresponding test suite is stored in [tests/test_gecodb_parser.py](tests/test_gecodb_parser.py). 

* The Python checkers for potential and actual applicability of the restrictive (L2P) constraints are stored in [check_applicability/l2p_satisfaction_checkers.py](check_applicability/l2p_satisfaction_checkers.py). The checkers rely on the GermaNet search functions scripted in [data_utils/germanet_search.py](data_utils/germanet_search.py). The tests for the checkers are in [tests/test_l2p_satisfaction_checkers.py](tests/test_l2p_satisfaction_checkers.py).

* For compound modeling, we used three theoretical accounts: regularity-based `AH02` (Albright & Hayes 2002), coverage-based `Y16-cvg` (Yang 2016), and condition-specificity-based `Y16-cond` (Yang 2016). The modeling included constraint ranking by the method's confidence parameter and iterative application of the ranked constraints in accordance with the Elsewhere Condition. During the modeling, all constraint conflicts and their resolutions were recorded. The script that implemented the theoretical models is [comp_modeling/compxconstraints.py](comp_modeling/compxconstraints.py). The (deprecated) test for the models should have been in [tests/test_compxconstraints.py](tests/test_compxconstraints.py). The three models with different configurations were run in [comp_modeling/main-modeling.py](comp_modeling/main-modeling.py).

* For LLM experiments, we used GLM-5.3-Flash . The inference ran with GMI Cloud. For shared LLM operations (initialization, completion, etc.), we created [comp_modeling/llm_utils.py](comp_modeling/llm_utils.py). To use the cloud, we first obtained an API key; the .env template for its storage is in [.env.template](.env.template). The prompts for the LLM are in [comp_modeling/prompts.py](comp_modeling/prompts.py).

* Before we ran the LLM on the constraint ranking task, we evaluated its general compounding competence with a linker prediction task. The code for that can be found in [comp_modeling/main-llm-benchmarking.py](comp_modeling/main-llm-benchmarking.py).

* To evaluate both the theoretical models and the LLMs in the linker prediction task, a number of metrics were developed in [comp_modeling/metrics.py](comp_modeling/metrics.py).

* We employed the LLM to rank constraints in [comp_modeling/main-llm-experiment.py](comp_modeling/main-llm-experiment.py).

* We classified the reasoning passages of the LLM that it returned during the constraint ranking task to match it with our three theoretical models, in [comp_modeling/main-llm-class-rank.py](comp_modeling/main-llm-class-rank.py).


### Output & Results

* The unresolved generative constraint conflicted are stored in [out/acceptable_linkers.json](out/acceptable_linkers.json). This is not an output of any specific model but rather an input to the models.

* The outputs of the three theoretical model experiment are stored in directories [out/albright-hayes](out/albright-hayes), [out/yang-cvg](out/yang-cvg), and [out/yang-cond](out/yang-cond), respectively. For each model, there are nine configurations. As it turned out during the experiment, the configurations produce effectively identical results, which is why you may concentrate on the best results stored at the root of each of these three directories. There, the most important files are the following: f1_acc_df.tsv (performance metrics), linker_scoreboards.json (final rankings from the model), preds.tsv (all final predictions), and production_summary.txt (resolutions of all unique conflicts). 

* The outputs of the LLM are stored in the [out/GLM-5.3-Flash](out/GLM-5.3-Flash) directory. Specifically, [out/GLM-5.3-Flash/linker_benchmark](out/GLM-5.3-Flash/linker_benchmark) contains th outputs of the model for the linker prediction task (predictions in [out/GLM-5.3-Flash/linker_benchmark/preds.tsv](out/GLM-5.3-Flash/linker_benchmark/preds.tsv) and metrics in [out/GLM-5.3-Flash/linker_benchmark/f1_acc_df.tsv](out/GLM-5.3-Flash/linker_benchmark/f1_acc_df.tsv)). [out/GLM-5.3-Flash/constraint_ranking.jsonl](out/GLM-5.3-Flash/constraint_ranking.jsonl) contains rankings of the constraints as ranked by the LLM with reasoning. [out/GLM-5.3-Flash/principle_classification.jsonl](out/GLM-5.3-Flash/principle_classification.jsonl) classifies these reasoning passages into the three theoretical accounts. Importantly, we also used the rankings to predict the linker similar to the theoretical accounts: see [out/GLM-5.3-Flash/preds_from_rankings](out/GLM-5.3-Flash/preds_from_rankings) (predictions missing, metrics in [out/GLM-5.3-Flash/preds_from_rankings/f1_acc_df.tsv](out/GLM-5.3-Flash/preds_from_rankings/f1_acc_df.tsv)). Since this procedure is deterministic, you can always elicit these predictions from the LLM rankings in the inspection notebook (see below).

* The [out](out) directory additionally contains a large number of figures, metrics, tables, etc. Follow the inspection notebook (see below) to understand their nature.

* Notebook [comp_modeling/inspect.ipynb](comp_modeling/inspect.ipynb) is designed to inspect and analyze the obtained results. The notebook contains detailed explanations, refer to it for the analysis procedures and description of the output files. An extraction from the notebook with the most important fragments is available in [out/comp_modeling_res.pdf](out/comp_modeling_res.pdf), and an even shorted version in [out/comp_modeling_res_short.pdf](out/comp_modeling_res_short.pdf).


### UNC-Tübingen Workshop Slides

* Please find the slides and the supplementary materials (the latter in the private version only) in [unc_workshop/slides](unc_workshop/slides).


## Reproducibility

_Please note that due to the copyright restrictions on CELEX-nouns (as a derivative of CELEX2) and GermaNet, you can only reproduce the study if you have an access to these datasets in compliance with their licenses: [CELEX2](https://catalog.ldc.upenn.edu/docs/LDC96L14/celex.readme.html#Copyright), [GN](https://uni-tuebingen.de/fakultaeten/philosophische-fakultaet/fachbereiche/neuphilologie/seminar-fuer-sprachwissenschaft/arbeitsbereiche/assoziierte-forschergruppen/seniorprofessur-hinrichs/ressourcen/lexica/germanet/lizenzen/)._

### Setup

1. Clone the repo and switch to the required branch:

    ```bash
    git clone https://github.com/maxschmaltz/DieKonstraints.git
    git checkout init_comp_modeling_sep26
    ```

2. Initialize a virtual environment and install requirements with a package manager of your choice. For my case (pip, Mac):

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```


### Data Preparation

* If you want to access the (partially manually) preprocessed CELEX-nouns, contact me to obtain a copy of it. Once again, it is only possible if you have an access to the original CELEX2 in comliance with its [license](https://catalog.ldc.upenn.edu/docs/LDC96L14/celex.readme.html#Copyright). Refer to the [GermaNet licensing page](https://uni-tuebingen.de/fakultaeten/philosophische-fakultaet/fachbereiche/neuphilologie/seminar-fuer-sprachwissenschaft/arbeitsbereiche/assoziierte-forschergruppen/seniorprofessur-hinrichs/ressourcen/lexica/germanet/lizenzen/) for the instructions on how to obtain a copy of the wordnet. The merged applicability index is available under [resources/developed/merged_geco_sp_appl_ind.tsv](resources/developed/merged_geco_sp_appl_ind.tsv).

* Alternatively, if you want to rebuilt the merged applicability index, you can unzip the applicability indices in [resources/semrel_comp_corp_study-private/appl_inds](resources/semrel_comp_corp_study-private/appl_inds) and run the data preprocessing script (see above):

    ```bash
    python3 -m data_utils.prepare_merged_geco_sp_appl_ind
    ```


### Experiments & Analysis

1. Run the modeling with the theoretical accounts:

    ```bash
    python3 -m comp_modeling.main-modeling
    ```

    The results will appear in the three respective directories in [out](out).

2. Benchmark the LLM on the linker prediction task, run the model to rank constraints, and classify its reasoning:

    ```bash
    python3 -m comp_modeling.main-llm-benchmarking
    python3 -m comp_modeling.main-llm-experiment
    python3 -m comp_modeling.main-llm-class-rank
    ```

    _As a prerequisite for the LLM experiments, you need to create an account with the [GMI Cloud](https://console.gmicloud.ai), get an API key, and put it in the .env file in accordance with the [.env.template](.env.template). Please note that the outputs of these experiments are not deterministic due to the probabilistic sampling of the LLM, so your results may be slightly different from ours._

3. Follow the [comp_modeling/inspect.ipynb](comp_modeling/inspect.ipynb) notebook for inspection & analysis. It will produce the remaining output files.


## References

_NB! Constraint & data sources are excluded, refer to Shmalts 2026 and Shmalts in preparation for them. These references concern modeling of (irregular) linguistic phenomena with theoretical models and LLMs only._

_Disclaimer: these references were converted from [comp_modeling/papers/references.bib](comp_modeling/papers/references.bib) with [BibTeX to Chicago converter](https://www.bibtex.com/c/bibtex-to-chicago-converter/)_.

* Albright, Adam, and Bruce Hayes. “Modeling English Past Tense Intuitions with Minimal Generalization.” Proceedings of the ACL-02 Workshop on Morphological and Phonological Learning - Volume 6 (USA), MPL ’02, 2002, 58–69. https://doi.org/10.3115/1118647.1118654.
* Albright, Adam, and Bruce Hayes. “Rules vs. Analogy in English Past Tenses: A Computational/Experimental Study.” Cognition 90, no. 2 (2003): 119–61. https://doi.org/10.1016/S0010-0277(03)00146-X.
* Albright, Adam. “A Quantitative Study on Spanish Paradigm Gaps.” In WCCFL 22 Proceedings, edited by G. Garding and M. Tsujimura. Cascadilla Press, 2003.
* Baer-Henney, Dinah, and Ruben van de Vijver. “Breaking Well -- Syllabification Strategies in German Speakers.” Preprint, London, UK, 2018.
* McCurdy, Kate, Sharon Goldwater, and Adam Lopez. “Inflecting When There’s No Majority: Limitations of Encoder-Decoder Neural Networks as Cognitive Models for German Plurals.” In Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics, edited by Dan Jurafsky, Joyce Chai, Natalie Schluter, and Joel Tetreault. Association for Computational Linguistics, 2020. https://doi.org/10.18653/v1/2020.acl-main.159.
* Neef, Martin, and Susanne R. Borgwaldt. “Fugenelemente in Neugebildeten Nominalkomposita.” In Strukturelle Eigenschaften Und Systembezogene Aspekte, edited by Livio Gaeta and Barbara Schlücker. De Gruyter, 2012. https://doi.org/10.1515/9783110278439.27.
* Yang, Charles. The Price of Linguistic Productivity: How Children Learn to Break the Rules of Language. The MIT Press, 10 2016. https://doi.org/10.7551/mitpress/9780262035323.001.0001.