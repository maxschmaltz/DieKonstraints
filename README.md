# Constraints on Linking Element Choice in German Nominal Compounding: A Large-Scale Corpus Study

> Compounding Constraints. Corpus Study. Nov25-Mar26

Paper for the [SLiDE Workshop](https://www.slide-workshop.org) @ [LREC26](https://lrec2026.info).


## Abstract

The N+N compound class is the largest and the most productive class of compounds in German. A significant number of N+N compounds insert a so-called linking element from a large inventory. The linker choice is notoriously irregular; instead of rules, it is governed by a set of constraints that can only limit this choice based on morphological, phonological, sometimes semantic and lexical properties of the first constituent. While constraints on linking element choice in German nominal compounding are extensively researched and well-documented, no large-scale corpus study has ever been reported on the subject of their empirical application. The present work aims at filling in this gap by conducting an extensive corpus study on potential and actual applicability of these constraints. The study summarizes 64 constraints collected from the relevant literature and obtains applicability statistics for 39 of them over 280k+ German N+N compounds. The study both confirms most of the evidence from previous literature and suggests novel evidence on German nominal compounding. It additionally highlights the importance of structured linguistic data for large-scale empirical studies.


## Code Structure

### Constraints

* The scientific sources from which the original constrain definitions were collected can be found in [constraints/references.bib](constraints/references.bib) (BibTex). The corresponding PDFs are stored in [constraints/papers/](constraints/papers/) (only in the private version).

* The summarized and classified constraints gathered from this relevant literature (see section 4.1 of the [paper](Constraints%20on%20Linking%20Element%20Choice%20in%20German%20Nominal%20Compounding.%20A%20Large-Scale%20Corpus%20Study.pdf)) are to be found in [constraints/constraints.yaml](constraints/constraints.yaml). This YAML has a dedicated README inside, refer to it for the structure and the adopted notation of this file.

* [constraints/evidence_dict.json](constraints/evidence_dict.json) maps the scientific sources to the summarized constraints they covered.

* Our suggestions to constraint corrections (see section 5 of the [paper](Constraints%20on%20Linking%20Element%20Choice%20in%20German%20Nominal%20Compounding.%20A%20Large-Scale%20Corpus%20Study.pdf)) are in [constraints/constraint_corrections.yaml](constraints/constraint_corrections.yaml). Similarly, the file has a dedicated README inside.


### Data

* We used two original datasets for our corpus study: CELEX2 (`baayen_etal_1995`) found in [resources/Celex/](resources/Celex/) and DeCOW16AX-comps (`schaefer_pankratz_2018`) in [resources/DeCOW16AX-comps/](resources/DeCOW16AX-comps/). Both sources are unavailable in the public version due to the copyright restrictions. DeCOW16AX-comps can, however, be accessed under https://doi.org/10.5281/zenodo.1323211. _Please note that in our research we used a version of DeCOW16AX-comps we had previously formatted in a different research, so the data from the original source diverges slightly._

* For the experiments, we first preprocessed both datasets (more details in section 4.3 of the [paper](Constraints%20on%20Linking%20Element%20Choice%20in%20German%20Nominal%20Compounding.%20A%20Large-Scale%20Corpus%20Study.pdf)). Files [data_utils/prepare_celex.py](data_utils/prepare_celex.py) and [data_utils/prepare_gecodb.py](data_utils/prepare_gecodb.py) contain code for preprocessing of CELEX2 and DeCOW16AX-comps, respectively. The files also contain explanations about the structure and the contents of the original datasets.

* The two preprocessed datasets (called CELEX-nouns and GeCoDB_v06, respectively) are stored in [resources/developed/celex_nouns.tsv](resources/developed/celex_nouns.tsv) (not available publicly due to the copyright restrictions) and [resources/developed/gecodb_v06.tsv](resources/developed/gecodb_v06.tsv), respectively. _NB! The preprocessed datasets have additionally undergone some manual cleaning/correction so the preprocessing code will produce similar but not identical output data._

* During the preprocessing, word counts of the entries of both datasets were inferred from DeReKo (`ids_2026`) (more details in section 4.3 of the [paper](Constraints%20on%20Linking%20Element%20Choice%20in%20German%20Nominal%20Compounding.%20A%20Large-Scale%20Corpus%20Study.pdf)); the code for that procedure can be found in [data_utils/dereko_search.py](data_utils/dereko_search.py), and [resources/developed/dereko_de_geq70_counts.tsv](resources/developed/dereko_de_geq70_counts.tsv) contains the inferred word counts.


### Experiments & Tests

* The code for parsing compounds (in GeCoDB_v06 notation) is available in [data_utils/gecodb_compound_parser.py](data_utils/gecodb_compound_parser.py), and the corresponding test suite is stored in [tests/test_gecodb_parser.py](tests/test_gecodb_parser.py). 

* The Python checkers for potential and actual applicability of the constraints (as described in sections 4.2 and 4.4 of the [paper](Constraints%20on%20Linking%20Element%20Choice%20in%20German%20Nominal%20Compounding.%20A%20Large-Scale%20Corpus%20Study.pdf)) are stored in [check_applicability/applicability_checkers.py](check_applicability/applicability_checkers.py). The checkers for the suggested corrected constraint are also in this file. The checkers are subscribed with the ids and summaries of the corresponding constraints. The tests for the checkers are in [tests/test_applicability_check_comp.py](tests/test_applicability_check_comp.py).

* The code for running the main experiment (see sections 4.2 and 4.4 of the [paper](Constraints%20on%20Linking%20Element%20Choice%20in%20German%20Nominal%20Compounding.%20A%20Large-Scale%20Corpus%20Study.pdf)) and for verification of the suggested corrected constraints (section 5 of the [paper](Constraints%20on%20Linking%20Element%20Choice%20in%20German%20Nominal%20Compounding.%20A%20Large-Scale%20Corpus%20Study.pdf)) can be found in [check_applicability/check_applicability.py](check_applicability/check_applicability.py) and [check_applicability/check_correction_suggestions.py](check_applicability/check_correction_suggestions.py), respectively.


### Output & Results

* The outputs of the main experiment are stored in [out/applicability_statistics/appl_index.zip](out/applicability_statistics/appl_index.zip) (to be unzipped) and [out/applicability_statistics/constr_statistics.tsv](out/applicability_statistics/constr_statistics.tsv). The first file indicates (whenever possible, so only for the 39 investigated constraints) potential and (if applicable) actual applicability of every constraint. It is organized as a series of triplets `<item_i: str, pa_i: bool, aa_i: bool>`, where `item` is the target item of constraint `i` in the corresponding compound (as defined in section 4.1 of the [paper](Constraints%20on%20Linking%20Element%20Choice%20in%20German%20Nominal%20Compounding.%20A%20Large-Scale%20Corpus%20Study.pdf)), and `pa_i` and `aa_i` indicate its potential and actual applicability to this compound, respectively; whenever a value is missing, an empty string is inserted instead. Thus, each row of the table looks like `compound, item_1: str, pa_1: bool, aa_1: bool, item_2: str, pa_2: bool, aa_2: bool, ..., item_n: str, pa_n: bool, aa_n: bool`. The second file contains the coverage and regularity statistics for the 39 constrains. For each constraint, it provides the number of unique target items for it in the dataset, the textual quantifier from its summarized definition, and then the item and type coverage and regularity values. Additionally, [out/applicability_statistics/constr_statistics_legacy.tsv](out/applicability_statistics/constr_statistics_legacy.tsv) contains a legacy version of this statistics that features a token variant of the measures.

* The outputs of the experiment with the suggested corrected constraints are stored in [out/applicability_statistics/appl_index_corr.zip](out/applicability_statistics/appl_index_corr.zip) and [out/applicability_statistics/constr_statistics_corr.tsv](out/applicability_statistics/constr_statistics_corr.tsv). The files have the same structure as the corresponding main experiment files.

* Notebook [check_applicability/inspect.ipynb](check_applicability/inspect.ipynb) is designed to inspect and analyze the obtained results. As a way to fix the findings, it creates a line of files in the [out/](out/) folder: actually, all the files except for the five files from the previous two bullet points. The notebook contains detailed explanations, refer to it for the analysis procedures and description of the output files.


### Paper

* [src/](src/) contains LaTex source for the paper, and the paper itself is in [Constraints on Linking Element Choice in German Nominal Compounding. A Large-Scale Corpus Study.pdf](Constraints%20on%20Linking%20Element%20Choice%20in%20German%20Nominal%20Compounding.%20A%20Large-Scale%20Corpus%20Study.pdf).


### Slides

* [slides/](slides/) contains the slides for the oral presentation at the SLiDE workshop at LREC26 ([LREC Talk Slides.key](slides/LREC%20Talk%20Slides.key)) as well as supplementary material (only in the private version).


## Reproducibility

_Please note that due to the copyright restrictions on CELEX2, you can only reproduce the research if you have an access to it in compliance with its [license](https://catalog.ldc.upenn.edu/docs/LDC96L14/celex.readme.html#Copyright)._

### Setup

1. Clone the repo and switch to the required branch:

    ```bash
    git clone https://github.com/maxschmaltz/DieKonstraints.git
    git checkout comp_constr_corp_study_mar26
    ```

2. Initialize a virtual environment and install requirements with a package manager of your choice. For my case (pip, Mac):

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```


### Data Preparation

* If you want to operate over the (partially manually) preprocessed CELEX-nouns used in the original research, contact me to obtain a copy of it. Once again, it is only possible if you have an access to the original CELEX2 in comliance with its [license](https://catalog.ldc.upenn.edu/docs/LDC96L14/celex.readme.html#Copyright). Our (partially manually) preprocessed GeCoDB_v06 is available under [resources/developed/gecodb_v06.tsv](resources/developed/gecodb_v06.tsv).

* Alternatively, if you want to rebuilt the data, you can do so with the data preprocessing scripts (see above). There are a few prerequisites for that:
    * For CELEX-nouns: You have a copy of the original CELEX2.
    * For GeCoDB_v06: the preprocessing code for DeCOW16AX-comps is designed for a formatted version of it which you have to obtain by contacting me.
    * For DeReKo: You are registered at IDS and have an API key for it (details in comments in [data_utils/dereko_search.py](data_utils/dereko_search.py)).

    _Please note the if you choose to rebuild the data, the experiments will produce slightly different results due to the missing manual cleaning/correction steps; also a couple of tests will fail for the same reason._


### Experiments & Analysis

1. Run the main experiment (optionally: the experiment over the suggested corrected constraints) with the corresponding scripts (see above):

    ```bash
    python -m check_applicability.check_applicability
    python -m check_applicability.check_correction_suggestions
    ```

    The results will appear in [out/applicability_statistics/appl_index.zip](out/applicability_statistics/appl_index.zip) and [out/applicability_statistics/constr_statistics.tsv](out/applicability_statistics/constr_statistics.tsv) (also [out/applicability_statistics/appl_index_corr.zip](out/applicability_statistics/appl_index_corr.zip) and [out/applicability_statistics/constr_statistics_corr.tsv](out/applicability_statistics/constr_statistics_corr.tsv) if you ran the second experiment).

2. Unzip [out/applicability_statistics/appl_index.zip](out/applicability_statistics/appl_index.zip) ([out/applicability_statistics/appl_index_corr.zip](out/applicability_statistics/appl_index_corr.zip)).

3. Follow the [check_applicability/inspect.ipynb](check_applicability/inspect.ipynb) notebook for inspection & analysis. It will produce the remaining output files.


## References


* Gerhard Augst. 1975. Untersuchungen zum Morpheminventar der deutschen Gegenwartssprache. Narr, Tübingen.
* Marco Baroni, Johannes Matiasek, and Harald
Trost. 2002. Wordform- and Class-based Prediction of the Components of German Nominal Compounds in an AAC System. InCOLING 2002: The 19th International Conference on Computational Linguistics.
* Peter Eisenberg. 2013. Grundriss der deutschen Grammatik, 4 edition. J.B. Metzler Stuttgart, Stuttgart. EBook published 27 August 2016.
* Nanna Fuhrhop and Sebastian Kürschner. 2015. 32. Linking elements in Germanic, pages 568–582. De Gruyter Mouton, Berlin, München, Boston.
* Maria Koliopoulou. 2014. How close to syntax are compounds? Evidence from the linking element in German and Modern Greek compounds. Rivista di Linguistica, 26(2):51–70.
* Kristin Kopf. 2017. Fugenelement und Bindestrich in der Compositions-Fuge, pages 177–204. De Gruyter, Berlin, Boston.
* Andrea Krott et al. 2004. Probability in the Grammar of German and Dutch: Interfixation in Triconstituent Compounds. Language and Speech, 47(1):83–106. PMID: 15298331.
* Andrea Krott, et al. 2007. Analogical effects on linking elements in German compound words. Language and Cognitive Processes, 22(1):25–57.
* Sebastian Kürschner. Verfugung-s-nutzung kontrastiv. Zur Funktion der Fugenelemente im Deutschen und Dänischen. Tijdschrift voor Skandinavistiek, 26(2).
* Sebastian Kürschner. 2010. Fuge-n-kitt, voeg-en-mes,fuge-masse und fog-e-ord - Fugenelemente im Deutschen, Niederländischen, Schwedischen und Dänischen : ein Grenzfall der Morphologie im Sprachkontrast. (Linking elements in German, Dutch, Swedish, and Danish contrast). In Dammel, Antje; Kürschner, Sebastian; Nübling, Damaris (Hrsg.): Kontrastive Germanistische Linguistik, volume 206-209 of Germanistische Linguistik, pages 827–862. Olms, Hildesheim.
* Gary Libben et al. 2009. Interfixation in German compounds: What factors govern acceptability judgements? Rivista di Linguistica, 21(1):149–180.
* Martin Neef and Susanne R. Borgwaldt. 2012. Fugenelemente in neugebildeten Nominalkomposita, pages 27–56. De Gruyter, Berlin, Boston.
* Damaris Nübling and Renata Szczepaniak. 2008. On the way from morphology to phonology: German linking elements and the role of the phonological word. Morphology, 18(1):1–25.
* Damaris Nübling and Renata Szczepaniak. 2013. Linking elements in German Origin, Change, Functionalization. Morphology, 23(1):67–89.
* Lorelies Ortner and Elgin Müller-Bollhagen. 1991. Hauptteil 4 Substantivkomposita. De Gruyter, Berlin, Boston.
* Roland Schäfer. 2018. Einführung in die grammatische Beschreibung des Deutschen. Number 2 in Textbooks in Language Sciences. Language Science Press, Berlin.
* Roland Schäfer andElizabethPankratz. 2018. The plural interpretability of German linking elements. Morphology, 28(4):325–358.
* Carmen Scherer. 2012. Vom Reisezentrum zum Reise Zentrum. Variation in der Schreibung von N+N-Komposita, pages 57–82. De Gruyter, Berlin, Boston.
* Barbara Schlücker. 2023. Compounding and Linking Elements in Germanic.
* Barbara Schlücker. 2012. Die deutsche Kompositionsfreudigkeit. Übersicht und Einführung, pages 1–26. De Gruyter, Berlin, Boston.
* Helmut Schmid, Arne Fitschen, and Ulrich Heid. 2004. SMOR: A German Computational Morphology Covering Derivation, Composition, and Inflection. In Proceedings of the Fourth International Conference on Language Resources and Evaluation (LREC’04), Lisbon, Portugal. European Language Resources Association (ELRA).
* Heide Wegener. 2003. Entstehung und Funktion der Fugenelemente im Deutschen, oder: warum wir keine Autosbahn haben. Linguistische Berichte, 196:425–457.
* Heide Wegener. 2005. Das Hühnerei vor der Hundehütte: von der Notwendigkeit historischen Wissens in der Grammatikographie des Deutschen.

---

* Baayen, R. H. and Piepenbrock, R. and Gulikers, L. 1995. CELEX2. Linguistic Data Consortium, ISLRN 204-698-863-053-1. Web Download.
* IDS. 2026. Deutsches Referenzkorpus / Archiv der Korpora geschriebener Gegenwartssprache 2026-I. Leibniz-Institut für Deutsche Sprache. PID https://www.ids-mannheim.de/dereko. Release vom 19.01.2026.
* Schäfer, Roland and Pankratz, Elizabeth. 2018. Dataset: The plural interpretability of German linking elements ("Morphology"). Zenodo. PID https://doi.org/10.5281/zenodo.1323211.


## Citation

Coming soon...