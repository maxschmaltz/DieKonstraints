# LREC26

This file documents ideas we collected and exchanges I had at LREC26. Note that the summaries are opinions of the presenters and their answers to my questions that I transmit intact. The summaries are sorted by the day, and within a day by importance.


## SLiDE@LREC26 (11.05)

### [Fast and Flexible Example-based Treebank Search with Vector Symbolic Architectures](https://pustejovsky.github.io/slide-lrec2026/book.pdf#page=78) ★★★

> Roussel

The study investigates different operations on dense binary vectors for an effective similarity search. It argues that a certain level of "fussiness" may be helpful to capture vectors (and, correspondingly, items) with features that are not fully faithful to the query but can still be relevant.

* While Roussel's approach covers vector representation of semantic structures, it is expandable to any binary (0 and 1, or 1 and -1) vectors.
* As a result of constraint verification, we obtained a 39x280k table of actual applicability of every analyzed constraint against every compound (we have the same table for potential applicability as well). This table consists of boolean values, and such each compound can be represented as a 39-place binary vector, where _i_-th place will indicate whether _i_-th constraint is actually applicable to it or not. With Roussel's method, it is therefore theoretically possible to cluster the compounds by target applicable constraints (use a desired combination as the query), for example, to identify groups with same or **similar** (here is where the fussiness comes in handy!) constraint conflicts.
* More fine-grained encoding (e.g. specifically by the linguistic properties of the constraints) may allow to capture more subtle relations between the vectors.

</br>

* Alternative application of the method may be generation of nonce data with desired properties: 1) encode the target item with the desired properties (we want to create nonce items with the same properties) as a binary vector (e.g. phones by their manner and place of articulation); 2) generate all possible nonce combinations (e.g. all combinations of the available phones); 3) encode the nonce combinations the same way; 4) run the search with the required level of fussiness to find nonce combinations with the same or with similar properties (e.g. all combinations whose phones are ...).



### [Subevent Structure as a Predictor of Entity Identity Change in Procedural Text](https://pustejovsky.github.io/slide-lrec2026/book.pdf#page=66) ★★

> Rim & Pustejovsky

Didn't quite get what the study was about but it suggested me the following possible procedure to identify plural vs singular meaning of N1 in a compound: 1) reformulate the compound periphrastically (e.g. Kindergarten = ein Garten für Kinder); 2) employ some kind of co-occurrence analysis of the main terms in the periphrasis (how exactly?). For step 1, Rim recommended I take a look at [Ye et al. 2025](https://aclanthology.org/2025.emnlp-main.1315/).



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