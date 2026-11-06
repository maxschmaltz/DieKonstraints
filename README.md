# Semantic Cues in German Nominal Compounding (Chapter 1: _Schäfer & Pankratz 2018_)

> June 2026 - August 2026

Extension of the [original corpus study](https://github.com/maxschmaltz/DieKonstraints/tree/comp_constr_corp_study_mar26) on the material of _Schäfer & Pankratz 2018_.


## Abstract

A long debate in linguistic studies on Germanic languages has addressed the question of "pluralic" linkers in compounds, that is, linking elements that are formally identical to the plural marker of the first constituent (N1) of the compound. The central question of the debate is whether there is an association between the pluralic linkers and the plural interpretation of N1s. While such an effect was generally agreed on in Dutch (Schreuder et. al 1998, Banga et al. 2013), it was for a long time rejected in German (Koester et al. 2004). Another line of evidence, however, suggested that the plural effect in German is real. In their resonant paper, Schäfer & Pankratz 2018 demonstrated that the probability of a pluralic linker is higher after N1s that exhibit a plural reading; the association was then confirmed statistically.
A different body of literature investigated further semantic effects in compounding in Germanic languages. Krott et al. 2002 found a significant main effect of animacy and concreteness in predicting linkers in Dutch compounds. Along these lines, Eisenberg 2013 suggested that person and animal designations as N1s may favor linkers -(")er- and -e- in German.

This solid background suggests that semantics may play a role in German nominal compounding. Corresponding semantic constraints on linker choice were proposed in the literature. Expanding on Shmalts 2026, the present study verifies 16 semantic constraints on corpus data. Twelve pluralic constraints are verified over a dataset derived from Schäfer & Pankratz 2018 consisting of ~2.3k German N+N compounds. The four remaining semantic constraints are non-pluralic; they are verified over a derivative of the GeCoDB_v06 dataset from Shmalts 2026. From the 16 constraints, three were applicable to <= 3 compounds and were excluded. From the 13 remaining constraints, four are not confirmed by the corpus data; the rest of the constraints only reach a low level of regularity.

We run a linear regression over the regularity of the constraints as the dependent variable and the types of linguistic information they access as the independent variable. The model converges and is significant at a p-value of 0.026. Among the five linguistic domains accessed by the constraints (morphology, derivation, phonology, semantics, lexic), only semantics main effect is significant (p-value 0.001). We find that accessing semantic information statistically decreases the regularity of a constraint by 0.2. Given this finding and the fact that all semantics-involving constraints verified in this study are coupled with a morphological condition, we conclude that semantics only has a complementary function in German nominal compounding and can only serve as a soft cue in linker prediction.


## Code Structure

### Constraints

* The scientific sources from which the original constrain definitions were collected can be found in [constraints/references.bib](constraints/references.bib) (BibTex). The corresponding PDFs are stored in [constraints/papers/](constraints/papers/) (only in the private version).

* The summarized and classified constraints gathered from this relevant literature (see section 4.1 of [Shmalts 2026](https://lrec.elra.info/lrec2026-ws-slide-02)) are to be found in [constraints/constraints_all_revised.yaml](constraints/constraints_all_revised.yaml). This version integrates the constraint corrections suggested in the original corpus study. This YAML has a dedicated README inside, refer to it for the structure and the adopted notation of this file. _IMPORTANT: on the contrary to the original corpus study, we do not suggest the corrections for the constraints. The reason for that is that the coverage of some semantic constraints was just too low to be conclusive. In the upcoming follow-up to this study (TODO: link), we will obtain our own annotations for the pluralic constraints, and only then will we suggest the corrections. What concerns the previously verified constraints, only a few of them turned out to be not fully supported after adopting a new (ir)regularity scale. None of these constraints required correction of the definitions (hence, checkers), and so we will simply adjust their quantifiers directly in the future versions (starting from the follow-up (TODO: link)); note that [Constraint Conflict Resolution in Neural Language Models: German Nominal Compounding](https://github.com/maxschmaltz/DieKonstraints/tree/init_comp_modeling_sep26) uses this list without the definition adjustments!_

* [constraints/evidence_dict_all_revised.json](constraints/evidence_dict_all_revised.json) maps the scientific sources to the summarized constraints they covered.


### Data

* To prepare the datasets used in the corpus experiments, we used the following resources:

    * CELEX2 (`baayen_etal_1995`): [resources/Celex/](resources/Celex/). The resource is unavailable in the public version due to the copyright restrictions.

    * CELEX-nouns is an derivative of CELEX2 built in [Shmalts 2026](https://github.com/maxschmaltz/DieKonstraints/tree/comp_constr_corp_study_mar26); it is stored in [resources/comp_constr_corp_study_mar26/celex_nouns.tsv](resources/comp_constr_corp_study_mar26/celex_nouns.tsv). For this study, we created a cleaner version of it which can be found in [resources/developed/celex_nouns.tsv](resources/developed/celex_nouns.tsv). The cleaning succeeded in [data_utils/prepare_celex_gecodb.py](data_utils/prepare_celex_gecodb.py). Both versions of CELEX-nouns are unavailable in the public version due to the copyright restrictions.

    * GermaNet v20.0: [resources/GermaNet/V200](resources/GermaNet/V200). Unavailable in the public version due to the copyright restrictions.

    * The central file used for the verification of the pluralic constraints is [resources/schaefer_pankratz_2018/Concordance.full.csv](resources/schaefer_pankratz_2018/Concordance.full.csv). It contains ~9.4k N+N compound tokens annotated by _Schäfer & Pankratz 2018_ for the collective meaning of their modifier; see chapter 4.2 of _Schäfer & Pankratz 2018_. The file is not distributed in our repo but can be retrieved from https://doi.org/10.5281/zenodo.1323211 (file 'linkingelements/Data/Corpusstudy/Concordance.full.csv'). We cleaned and preprocessed this dataset in [data_utils/prepare_sp18/prepare_sp18.py](data_utils/prepare_sp18/prepare_sp18.py), resulting in _SP18_: [resources/developed/sp18/sp18.tsv](resources/developed/sp18/sp18.tsv).

* Two lines of datasets were used in corpus experiments. The first line was used to reverify the constraints verified in the original corpus study to ensure its robustness:

    * _GeCoDB\_v06_ (~283k compound lemmata) from [Shmalts 2026](https://github.com/maxschmaltz/DieKonstraints/tree/comp_constr_corp_study_mar26): [resources/comp_constr_corp_study_mar26/gecodb_v06.tsv](resources/comp_constr_corp_study_mar26/gecodb_v06.tsv).

    * A cleaner derivative of _GeCoDB\_v06_ called _GeCoDB\_v07_ (~275k compound lemmata): [resources/developed/gecodb_v07.tsv](resources/developed/gecodb_v07.tsv). To create _GeCoDB\_v07_, we took the new version of CELEX-nouns and only kept compounds from _GeCoDB\_v06_ whose constituents were found there. This dataset was prepared in [data_utils/prepare_celex_gecodb.py](data_utils/prepare_celex_gecodb.py).

    * A "wordnet-curated" derivative of _GeCoDB\_v07_ called _GeCoDB\_v07\_GN_ (~49k compound lemmata): [resources/developed/gecodb_v07_gn.tsv](resources/developed/gecodb_v07_gn.tsv). This dataset includes only compounds from _GeCoDB\_v07_ that can be parsed in GermaNet v20.0 unambiguously. The code for parsing is in [data_utils/germanet_search.py](data_utils/germanet_search.py). This dataset was prepared in [data_utils/prepare_gecodb_v07_gn.py](data_utils/prepare_gecodb_v07_gn.py).

* The second line of the datasets covered 12 pluralic and 4 non-pluralic semantic constraints:

    * _GeCoDB\_v07\_GN_ (~49k compound lemmata) was also used to verify the 4 non-pluralic semantic constraints.

    * To verify the 12 pluralic constraints, we used a derivative of _SP18_ that we called _SP18\_Pl\_Constr_ (~2.3k compound lemmata). It was prepared in [data_utils/prepare_sp18/prepare_sp18_pl_constr.py](data_utils/prepare_sp18/prepare_sp18_pl_constr.py).

* The statistics of the four datasets used to (re-verify) the constraints are to be found in [data_utils/dataset_stats.ipynb](data_utils/dataset_stats.ipynb).

* A dedicated line of experimentation probed the external and internal plural effect as defined by _Schäfer & Pankratz 2018_. For that, two respective dataset collections were used:

    * [resources/developed/sp18/extpe](resources/developed/sp18/extpe) prepared from _SP18_ in [data_utils/prepare_sp18/prepare_sp18_extpe.py](data_utils/prepare_sp18/prepare_sp18_extpe.py).

    * [resources/developed/sp18/extpe](resources/developed/sp18/extpe) prepared from _SP18_ in [data_utils/prepare_sp18/prepare_sp18_intpe.py](data_utils/prepare_sp18/prepare_sp18_intpe.py).


* During the preprocessing, word counts of the entries of both datasets were inferred from DeReKo (`ids_2026`) (more details in section 4.3 of [Shmalts 2026](https://lrec.elra.info/lrec2026-ws-slide-02)); the code for that procedure can be found in [data_utils/dereko_search.py](data_utils/dereko_search.py), and [resources/developed/dereko_de_geq70_counts_lemmatized.tsv](resources/developed/dereko_de_geq70_counts_lemmatized.tsv) as well as [resources/developed/dereko_de_geq70_counts_nlemmatized.tsv](resources/developed/dereko_de_geq70_counts_nlemmatized.tsv) contains the inferred word counts. Read the comments in the [data_utils/dereko_search.py](data_utils/dereko_search.py) script to learn the difference.

* Helpers for loading the datasets are in [data_utils/load_datasets.py](data_utils/load_datasets.py).


### Experiments & Tests

* The code for parsing compounds (in GeCoDB_vXX notation) is available in [data_utils/gecodb_compound_parser.py](data_utils/gecodb_compound_parser.py), and the corresponding test suite is stored in [tests/test_gecodb_parser.py](tests/test_gecodb_parser.py).

* The Python checkers for potential and actual applicability of the constraints (as described in sections 4.2 and 4.4 of [Shmalts 2026](https://lrec.elra.info/lrec2026-ws-slide-02)) are stored in [check_applicability/applicability_checkers.py](check_applicability/applicability_checkers.py). The checkers are subscribed with the ids and summaries of the corresponding constraints. The tests for the checkers are in [tests/test_applicability_check_comp.py](tests/test_applicability_check_comp.py).

* This version used a new (ir)regularity scale based on the findings of _Yang 2016_. The implementation of this scale is in [check_applicability/regularity_scale.py](check_applicability/regularity_scale.py). The tests for the scale are available in [tests/test_regularity_scale.py](tests/test_regularity_scale.py).

* The code for running the main experiment can be found in [check_applicability/main.py](check_applicability/main.py).

* Probing of the external and the internal plural effect was done in [plural_effects/extpe_sp18.ipynb](plural_effects/extpe_sp18.ipynb) and [plural_effects/intpe_sp18.ipynb](plural_effects/intpe_sp18.ipynb), respectively.


### Output & Results

* The outputs of the main corpus study experiments are stored in [out/constraints](out/constraints):

    * There, a dedicated folder is created for each dataset, e.g. [out/constraints/applicability_statistics/gecodb_v06](out/constraints/applicability_statistics/gecodb_v06), [out/constraints/applicability_statistics/gecodb_v07](out/constraints/applicability_statistics/gecodb_v07), etc., which contains an applicability index (to be unzipped, e.g. [out/constraints/applicability_statistics/gecodb_v06/appl_index.zip](out/constraints/applicability_statistics/gecodb_v06/appl_index.zip)) and the applicability statistics (e.g. [out/constraints/applicability_statistics/gecodb_v06/appl_statistics.tsv](out/constraints/applicability_statistics/gecodb_v06/appl_statistics.tsv)). The first file indicates (whenever possible) potential and (if applicable) actual applicability of every constraint. It is organized as a series of triplets `<item_i: str, pa_i: bool, aa_i: bool>`, where `item` is the target item of constraint `i` in the corresponding compound (as defined in section 4.1 of [Shmalts 2026](https://lrec.elra.info/lrec2026-ws-slide-02)), and `pa_i` and `aa_i` indicate its potential and actual applicability to this compound, respectively; whenever a value is missing, an empty string is inserted instead. Thus, each row of the table looks like `compound, item_1: str, pa_1: bool, aa_1: bool, item_2: str, pa_2: bool, aa_2: bool, ..., item_n: str, pa_n: bool, aa_n: bool`. The second file contains the coverage and regularity statistics for the verified constrains. For each constraint, it provides the number of unique target items for it in the dataset, the textual quantifier from its summarized definition, and then the item and type coverage and regularity values.

    * An aggregated statistics summary over all four dataset is in [out/constraints/applicability_statistics/appl_statistics_summary.tsv](out/constraints/applicability_statistics/appl_statistics_summary.tsv).

    * Notebook [check_applicability/inspect.ipynb](check_applicability/inspect.ipynb) is designed to inspect and analyze the obtained results. As a way to fix the findings, it creates a large line of files in the [out/constraints](out/constraints) folder. The notebook contains detailed explanations, refer to it for the analysis procedures and description of the output files. Two short PDF versions of the notebook are also stored in [out/constraints/constraints_corp_study.pdf](out/constraints/constraints_corp_study.pdf) and [out/constraints/constraints_corp_study_chapter_3.pdf](out/constraints/constraints_corp_study_chapter_3.pdf), respectively.

* The outputs of the probing of the external and the internal plural effect are stored in [out/extpe_sp18](out/extpe_sp18) and [out/intpe_sp18](out/intpe_sp18), respectively. The notebooks for the probing contain exhaustive descriptions of those. Short PDF versions of the notebooks are in [out/extpe_sp18/extpe_sp18_res.pdf](out/extpe_sp18/extpe_sp18_res.pdf) and [out/intpe_sp18/intpe_sp18_res.pdf](out/intpe_sp18/intpe_sp18_res.pdf).



## Reproducibility

_Please note that due to the copyright restrictions on CELEX2, you can only reproduce the research if you have an access to it in compliance with its [license](https://catalog.ldc.upenn.edu/docs/LDC96L14/celex.readme.html#Copyright)._

### Setup

1. Clone the repo and switch to the required branch:

    ```bash
    git clone https://github.com/maxschmaltz/DieKonstraints.git
    git checkout semcue_comp_sp18_aug26
    ```

2. Initialize a virtual environment and install requirements with a package manager of your choice. For my case (pip, Mac):

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```


### Data Preparation

* If you want a copy of preprocessed CELEX-nouns used in the present study, contact me to obtain a copy of it. Once again, it is only possible if you have an access to the original CELEX2 in comliance with its [license](https://catalog.ldc.upenn.edu/docs/LDC96L14/celex.readme.html#Copyright). Visit the [GermaNet webpage of the University of Tübingen](https://uni-tuebingen.de/en/faculties/faculty-of-humanities/departments/modern-languages/department-of-linguistics/chairs/associated-research-groups/general-and-computational-linguistics/ressources/lexica/germanet/licenses/) to learn how to obtain a copy of GermaNet. The annotated _Schäfer & Pankratz 2018_ data is available under https://doi.org/10.5281/zenodo.1323211 (file 'linkingelements/Data/Corpusstudy/Concordance.full.csv'). All other datasets are available in the public version of this repository as described in [section Data](#data).

* Alternatively, if you want to rebuilt the data, you can do so with the data preprocessing scripts (see [section Data](#data)). There are a few prerequisites for that:
    * For CELEX-nouns: You have a copy of the original CELEX2 and a copy of GermaNet.
    * For GeCoDB_v07 and GeCoDB_v07_GN: You have a copy of CELEX-nouns and of GermaNet.
    * For DeReKo: You are registered at IDS and have an API key for it (details in comments in [data_utils/dereko_search.py](data_utils/dereko_search.py)).


### Experiments & Analysis

* For constraint verification:

    1. Run the main experiment:

        ```bash
        # python3 -m check_applicability.main
        ```

        The results will appear in [out/constraints](out/constraints).

    2. Follow the [check_applicability/inspect.ipynb](check_applicability/inspect.ipynb) notebook for inspection & analysis. It will produce the remaining output files.

* For probing the external/internal plural effect: follow the [plural_effects/extpe_sp18.ipynb](plural_effects/extpe_sp18.ipynb) and [plural_effects/intpe_sp18.ipynb](plural_effects/intpe_sp18.ipynb) notebooks.


### References & Citation:

TODO