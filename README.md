# DieKonstraintsPrivat


This repository is dedicated to a long-term project called **The Status of Linguistic Constraints in Neural Language Models**. It contains (sub)projects that are incremental steps of the project or are related to it otherwise. Each (sub)project is hosted on a dedicated branch of this repository; please visit the branch of a specific (sub)project for more details about it.

* [Overall Abstract](#overall-abstract)
* [Projects](#projects)


## Overall Abstract

We want to investigate the extent to which generative language models (LMs) are capable of acquiring abstract linguistic knowledge beyond the factual information presented in the training data. By abstract linguistic knowledge, we mean knowledge about linguistic mechanisms and patterns acquired by LMs without being explicitly trained for it. Recent linguistic studies suggest that LMs exhibit such abstraction capabilities over linguistic rules. Given this promising state of the art, we want to investigate whether such abstraction capabilities also extend to sets of interacting linguistic constraints in phonology and morphology that can be in conflict with one another and that thus require constraint conflict resolution.

We want to explore to what extent current transformer models can already capture such constraint interactions. Specifically, we want to address the following research questions: 1) Are transformer-based generative LMs able to abstract linguistic constraints from the training data? 2) If abstraction capabilities are confirmed, how similar are the abstracted constraints to the frameworks established in the linguistic literature? 3) If abstraction capabilities are not confirmed, how does explicit insertion of constraints in the prompt change the model generations? By addressing these questions, we strive to make novel and innovative contributions to the research questions summarized under the rubrics LM capabilities, Ontological Status, and Explanatory Potential of the Priority Programme.

We carefully chose three linguistic phenomena such that the complexity of the constraint space governing these phenomena is suitably diverse. All three phenomena can be formalized as a sequence-to-sequence task of generating the most probable output string given an input sequence. This makes them ideally suited for an LM analysis. Investigating the constraint interaction for each of these phenomena with LMs can provide a cue about the abstraction capabilities of LMs. Our main hypothesis for this study is: transformer-based generative LMs do abstract and generalize linguistic constraints from the training data. We furthermore predict a negative correlation between the complexity of the constraint space for a phenomenon, and the extent to which LMs abstract these constraints.

To evaluate our hypotheses, we will adopt a set of methods from mechanistic interpretability studies. Specifically, we will be 1) producing possible output variants, resulting from different constraint violations on the input, and 2) inspecting the probabilities assigned to them by LMs, in different settings. This will allow us to mitigate the interference of factual knowledge and concentrate on abstract linguistic knowledge acquired by LMs.



## Projects


### [The Status of Linguistic Constraints in Neural Language Models](https://github.com/maxschmaltz/DieKonstraints/tree/dfg_proposal_sep25) | Aug25-Sep25

Proposal to the [LaSTing priority program of the DFG](https://www.dfg.de/de/aktuelles/neuigkeiten-themen/info-wissenschaft/2025/ifw-25-32). The public version only contains the abstract of the proposal and the references.

> \<Abstract identical to the [Overall Abstract](#overall-abstract)\>


### [Constraints on Linking Element Choice in German Nominal Compounding: A Large-Scale Corpus Study](https://github.com/maxschmaltz/DieKonstraints/tree/comp_constr_corp_study_mar26) | Nov25-Mar26

Paper for the [SLiDE Workshop](https://www.slide-workshop.org) @ [LREC26](https://lrec2026.info).

> The N+N compound class is the largest and the most productive class of compounds in German. A significant number of N+N compounds insert a so-called linking element from a large inventory. The linker choice is notoriously irregular; instead of rules, it is governed by a set of constraints that can only limit this choice based on morphological, phonological, sometimes semantic and lexical properties of the first constituent. While constraints on linking element choice in German nominal compounding are extensively researched and well-documented, no large-scale corpus study has ever been reported on the subject of their empirical application. The present work aims at filling in this gap by conducting an extensive corpus study on potential and actual applicability of these constraints. The study summarizes 64 constraints collected from the relevant literature and obtains applicability statistics for 39 of them over 280k+ German N+N compounds. The study both confirms most of the evidence from previous literature and suggests novel evidence on German nominal compounding. It additionally highlights the importance of structured linguistic data for large-scale empirical studies.