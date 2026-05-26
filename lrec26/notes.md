# LREC26

This file documents ideas we collected and exchanges I had at LREC26. The opinions/findings etc. of the presenters and their answers to my questions are given in the bullet points; I transmit them intact. My comments and conclusions are pre- and appended in plain text. The summaries are sorted by the day, and within a day by importance.

Summaries (or their fragments) that are already incorporated into the working plan are marked with small text.


## SLiDE@LREC26 (11.05)

### [Fast and Flexible Example-based Treebank Search with Vector Symbolic Architectures](https://pustejovsky.github.io/slide-lrec2026/book.pdf#page=78) ★★★

> Roussel

The study investigates different operations on dense binary vectors for an effective similarity search. It argues that a certain level of "fussiness" may be helpful to capture vectors (and, correspondingly, items) with features that are not fully faithful to the query but can still be relevant.

* While Adam Roussel's approach covers vector representation of semantic structures, it is expandable to any binary (0 and 1, or 1 and -1) vectors.
* As a result of constraint verification, we obtained a 39x280k table of actual applicability of every analyzed constraint against every compound (we have the same table for potential applicability as well). This table consists of boolean values, and such each compound can be represented as a 39-place binary vector, where _i_-th place will indicate whether _i_-th constraint is actually applicable to it or not. With Adam Roussel's method, it is therefore theoretically possible to cluster the compounds by target applicable constraints (use a desired combination as the query), for example, to identify groups with same or **similar** (here is where the fussiness comes in handy!) constraint conflicts.
* More fine-grained encoding (e.g. specifically by the linguistic properties of the constraints) may allow to capture more subtle relations between the vectors.

</br>

* Alternative application of the method may be generation of nonce data with desired properties: 1) encode the target item with the desired properties (we want to create nonce items with the same properties) as a binary vector (e.g. phones by their manner and place of articulation); 2) generate all possible nonce combinations (e.g. all combinations of the available phones); 3) encode the nonce combinations the same way; 4) run the search with the required level of fussiness to find nonce combinations with the same or with similar properties (e.g. all combinations whose phones are ...).



### [Subevent Structure as a Predictor of Entity Identity Change in Procedural Text](https://pustejovsky.github.io/slide-lrec2026/book.pdf#page=66) ★★

<small>

> Rim & Pustejovsky

Didn't quite get what the study was about but it suggested me the following possible procedure to identify plural vs singular meaning of N1 in a compound: 1) reformulate the compound periphrastically (e.g. Kindergarten = ein Garten für Kinder); 2) employ some kind of co-occurrence analysis of the main terms in the periphrasis (how exactly?). For step 1, Kyeongmin Rim recommended I take a look at [Ye et al. 2025](https://aclanthology.org/2025.emnlp-main.1315/).

</small>



### [The L2 Network: A CEFR-Aligned Knowledge Graph for Grammar Domain Modeling](https://pustejovsky.github.io/slide-lrec2026/book.pdf#page=162) ★★

> Ribeiro-Flucht & Chen

The study compiled a knowledge graph for a narrow domain of CERF-centered educational materials for English grammar.

* Injecting the graph in a textual form (head - relation - tail) into a prompt for LLMs enhanced its domain knowledge. Not clear how to incorporate the graph as some kind of representation and not textually. 
* The graph was deterministic. Not clear how to encode a non-deterministic graph.



### [Modeling Word-Internal Structures: Morphological Segmentation Across 58 Languages](https://pustejovsky.github.io/slide-lrec2026/book.pdf#page=194) ★

> John et al.

The study used raw LSTMs for multilingual morphological segmentation.

* The LSTMs achieved approx. 0.8-0.9 overall accuracy score.
* German was one of the target languages, and German compounding and plural forms must have been covered. No accuracy score was provided specifically for these German phenomena, is, however, presumably on the same level.



### Unaffiliated ★

Someone suggested that linkers are so irregular due to diachronic standartization taking place right now. Correspondingly, partial standartization results in irregularities where compounds with the same/similar properties some have and some have not yet undergone standartization. He further suggested that a dialectal study may be useful to verify this hypothesis: maybe the dialects are more consistent with linker choice.




## Main Conference Day 1 (13.05)

### [Do Language Models Encode Semantic Relations? Probing and Sparse Feature Analysis](https://lrec.elra.info/lrec2026-main-166) ★★

<small>

> Diera & Scherp

The study aimed at answering the question whether LMs are capable od capturing meaning in a structured manner.

* Covered antonymy/synonymy, hypernymy/hyponymy.
* Directly prompted the model to answer whether a relation R holds between two entities ("Is dog a hyperonym for beagle?").
* Llama3.1 8B achieved an accuracy of 0.66-0.91 for different relations which might suggest that the model encodes the semantic relations but some are challenging for it.
* Overall, the models demonstrated consistently increasing difficulty in order antonymy - hyponymy - hypernymy - synonymy.
* Suggested to take a look at works of Barbara Plank (LMU).

Since even the small Llama3.1 8B detected antonymy quite easily, maybe we can formulate plural meaning identification for N1 as an antonymy detection task? E.g. Kindergarten = ein Garten für Kinder vs Kindergarten = ein Garten für ein Kind.

</small>


### [Are Language Models Borrowing-Blind? A Multilingual Evaluation of Loanword Identification across 10 Languages](https://lrec.elra.info/lrec2026-main-269) ★

> Silva & Ahmadi

The study was dedicated to automated loanword identification with LMs.

* Not quite clear how loanwords can be formalized to begin with, as some of the borrowing are too rooted in the language (e.g. 'Fenster' from Latin 'fenestra'). The study therefore concentrated on so-called "striking" loanwords - such that are confidently identified as loanwords by the speakers when confronted with a native equivalent: e.g. 'Computer' vs 'Rechner'.
* The first result of the study is the conclusion that identification of loanwords is not a solved NLP problem, and various open- and closed-source models only reach an F1-score ceiling of 0.47 when prompted zero-shot and 0.94 when fine-tuned (the latter is good but is probably caused by memorization).
* An counterintuitive finding was that suprisal for the loanwords was lower than that of the native words; in other words, the model the loanwords were more "expected" for the models. Dataset analysis revealed that at the same time, the native words were more frequent.

Maybe the last finding may be used as a basis for a loanword identification procedure that compares surprisal vs token probability of the words in the input sentence. Since surprisal of the models for the loanwords was high while their frequency was low, maybe tokens with both a low probability and (contradictorily) a low surprisal may point to loanwords?



### [The Impact of Tokenization Algorithms on Hungarian Language Model Performance](https://lrec.elra.info/lrec2026-main-199) ★

> Osváth et al.

The study investigates different morphologically informed and agnostic tokenizers for different downstream tasks.

* The metrics reveal that BPE results in the best morphology alignment while a morphologically informed version of Unigram LM achieves the best overall performance. However, the differences turn out to be statistically insignificant across all tasks across one. Correspondingly, there are scenarios where whether the tokenizer is morphologically informed or agnostic impacts the model performance.

Correspondingly, different tokenizers have to be tested for our phenomena.



## Main Conference Day 2 (14.05)

### [Orthographic Constraint Satisfaction and Human Difficulty Alignment in Large Language Models](https://lrec.elra.info/lrec2026-main-426) ★★★★★

> Tuck & Verma

The study tests various LMs in the task of word generation under given orthographic constraints. In this iteration, made-up strong constraints are targeted. They are formulated as a plain text within the prompt (e.g. "Generate words with characters [a, b, ...], length 4-7 characters, the 3rd character should be a vowel... "), and the task of the LM is to generate all words it can "think" of that satisfies it. At the same time, a daily puzzle app gathered generations from humans under the same constraints, and the generations were used as a gold standard.

* No constraints were violated in any of the LM-generated words but the word space was underexplored by them.
* Specifically, constraint-valid words with atypical orthography were missed by LMs (e.g. 'data' had 9% human vs 93% LM miss rate) => the LMs oriented much more on distributional plausibility rather than on constraint satisfaction.

In the further iterations, Bryan Tuck wants to expand the constraint space to investigate constraint overload: when will the model start violating constraints as their number increases? Overall, this is extremely relevant to our constraint conflict investigation.



### [Automatic Suggestions Help Extending Eventive Ontology: A Case Study on SynSemClass](https://lrec.elra.info/lrec2026-main-620) ★★★

<small>

> Straková et al.

There exists a verb scheme ontology (motion, causal, etc.) with about 1500 different schemes. Correspondingly, when a new verb is about to be added to the ontology, it should be assigned one of the schemes or, in case none fits it, a new scheme. The study used NNs to help extend the ontology in a semi-automatic manner.

* Different approaches to the task didn't work. Specifically, word similarity or 1500-label classification resulted in a low performance.
* The task was solved as a binary classification task. Thus, an NN was trained (on existing verb-scheme couplings) that returned 1500 boolean values for the input verb. _i_-th boolean indicated whether the verb may belong to the _i_-th scheme. If more than one schemes are marked with True, top _k_ schemes are retrieved and sorted by probability with a consecutive manual inspection; if all schemes return False, it may indicate that the verb belongs to a new scheme.
* For the problem of classification of semantic relations between N1 and N2, the same method may be exploited given sufficient data. This may be used to cluster compounds by the semantic relation between N1 and N2 (25-30 schemes expected, e.g. possessive, modification, copulative etc. meanings) to investigate the semantic relation effect on linker choice. To begin, we can seed three to five known relations and expand as we will be receiving compounds that belong to none of them. Alternatively, this may be used to identify plural/singular meaning of compounds (plural scheme vs singular scheme).
* If we don't find data (which most likely will be the case), we can try contrastive learning similar to word2vec. We can train a metric/embedding that will be predicting for two arbitrary compounds if they belong together or not, without knowing to which scheme exactly. To do so, we should train an NN in an unsupervised manner on contrastive pairs or a real compound (with some semantic relation between the N1 and N2) vs a nonce compound (where this relation does not hold at all). When this model learns to tell two compounds apart or together, we can cluster the whole space of real compounds by pairwise comparison. We can then inspect the resulting clusters manually to identify the semantic relations within the resulting groups.

</small>


### [Prompt-Based Stance Control in German: An Evaluation of LLMs for Experimental Research on Attitude Change](https://lrec.elra.info/lrec2026-main-644) ★

> Omiecienski et al.

The study is in general irrelevant to us, but Agnieszka Falenska recommended me to examine Sabine Schulte im Walde's work regarding the problematic of steering the model generations with irregular constraints. They are also at the University of Stuttgart, so Agnieszka Falenska invited for a visit some day (scientific politeness?).



### [Towards a Diagnostic and Predictive Evaluation Methodology for Sequence Labeling Tasks](https://lrec.elra.info/lrec2026-main-472) ★

> Alvarez-Mellado & Gonzalo

The paper suggests to evaluate groups of test inputs with different linguistic properties separately in order to enhance predictability of the model (will probably fail on inputs of group A and be good on inputs of group B) and actionability of evaluation (fails on group A, fine-tune/add heuristics etc. for linguistic properties of A).

* Evidence that the same model can fail on a certain task on inputs with one linguistic properties and simultaneously exhibit good performance on inputs with other.
* Different models can be sensitive to different properties, so a model A fails on X and is good on Y, while a model B is good on X but fails on Y.

This finding ties nicely with the fact that we have groups of inputs with different linguistic properties. It points out that we might want to evaluate these groups separately, as well. If we know which models deal well with which properties, we can assemble an ensemble model.



### [A Study on Building Efficient Zero-Shot Relation Extraction Models](https://lrec.elra.info/lrec2026-main-480) ★

<small>

> Thomas et al.

Not super relevant but suggested an idea similar to the one [Rim & Pustejovsky](#subevent-structure-as-a-predictor-of-entity-identity-change-in-procedural-text-) gave me: can we identify plural etc. N1 meaning by retrieving relations from the compound definitions in a dictionary? Or classify the definitions?

</small>



### [Evaluating LLM-based Text Simplification for German: Effects on Post-Editing Effort, Quality Ratings, and User Comprehension](https://lrec.elra.info/lrec2026-main-571) ★

<small>

> Carrer et al.

Interesting but irrelevant for us. However, a question arose: how do simplified German deal with compounds? Do it formulate them periphrastically? If so, can we used text simplification to produce periphrastic formulation for step 1 of the approach I formulated after listening to [Rim & Pustejovsky](#subevent-structure-as-a-predictor-of-entity-identity-change-in-procedural-text-)?

</small>


## Main Conference Day 3 (15.05)

### [Semantic Parsing for Evaluating Large Language Models: Separating Linguistic Abilities with YARN](https://lrec.elra.info/lrec2026-main-765) ★

> de Vergnette & Amblard

The study tests the abilities of different LMs to semantically parse the input sentence into a predefined semantic scheme that specifies various linguistic aspects separately (quantification, negation, tense, modality etc.). Each trial looks as follows. First, a YARN ([Pavlova et al. 2024](https://aclanthology.org/2024.dmr-1.8/)) representations of a few example sentences and the target sentence are flattened into JSON (and alternative format), and thus the corresponding semantic properties of the sentences are encoded in a structured manner. These representations are injected in the prompt, and the target sentence is given in plain text. The goal of the model is to create the same representation for the target sentence. The output representation is verified against the flattened YARN representation.

<small>

* The modular structure of YARN (flattened) representation allows to test for different linguistic aspects separately (quantification, negation, tense, modality etc.). It turns out that different aspects are parsed by different models with varying performance. Thus for example, a model A may be good at quantification and exhibit a poor quality at modality while another model B can be great at modality while failing at quantification.
</small>
* No tested model was good at all the aspects.
* The representation format also impacted the performance.

Confirms the main finding of [Alvarez-Mellado & Gonzalo](#towards-a-diagnostic-and-predictive-evaluation-methodology-for-sequence-labeling-tasks) in a different dimension.


### [Two Ojibwe Constraint Grammars: Morphological Disambiguation and Dependency Parsing](https://lrec.elra.info/lrec2026-main-766) ★

> Diederichsen & Hammerly

The study connects two constraint grammars to create a dependency parser for the low-resource language of Ojibwe. The first grammar is formalized as an FST that produces morphological annotations for the words in the input sentence (independently), and the second grammar is a constraint grammar that parses dependencies given the annotated sentence.

* The implemented CGs cover regular rules, and so both grammars are deterministic.
* For a non-deterministic CG with known probabilities I should take a look at [Bick & Didriksen 2015](https://aclanthology.org/W15-1807/).