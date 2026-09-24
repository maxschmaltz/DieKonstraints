PREDICT_LINKER_PROMPT = """\
You are a German native speaker and you help me \
with my homework. My task is to join two nouns into \
a compound noun existing in German. My textbook provides \
the following examples:

EXAMPLE 1
Nouns: 'Freund' and 'Kreis'
Variants: 'Freundekreis', 'Freundeskreis', 'Freundkreis'
Correct answer: 'Freundeskreis'

EXAMPLE 2
Nouns: 'Herz' and 'Bedürfnis'
Variants: 'Herzbedürfnis', 'Herzenbedürfnis', 'Herzensbedürfnis'
Correct answer: 'Herzensbedürfnis'

Below is the real task I have. Please help me and pick
the correct answer from the given Variants. There is always
only one correct answer in the Variants so make sure that you
find it exclusively among them. Only return the correct answer
without any tags, punctuation, or any other marks. Don't think
about the answer, return directly what you believe is the correct option.

REAL TASK
Nouns: '{n1}' and '{n2}'
Variants: {variants}
Correct answer: 
"""


# https://docs.z.ai/guides/capabilities/struct-output
format_description = """\
Format the response to the following JSON scheme:

{
    "ranking": List[int]: The correct ranking of the rules. Insert the ordinal number of the rules only.
    "principle": str: The principle that in used to rank these rules.
    "guess": str: Your guess on what noun I have in mind
}
"""

format_instructions = {
    "role": "system",
    "content": format_description
}


RANK_CONSTRAINTS_PROMPT = """\
German compounds created from two nouns sometimes insert a so-called \
linking element in between, for example, Blume + Topf = Blume+n+topf. \
The correct output is determined by a set of rules. The rules, however, \
may be in conflict, in which case a careful rule ranking is required; \
the top-ranked rule produces the output.

Here's an example of conflict and different resolutions:
*. Compounds belonging to technical terminology (economics, law, medicine, etc.) \
are often missing an explicit linking element. Acceptable linking elements: -0-.
*. First constituents that are constituted by derived nouns with suffixes \
-(ig)keit, -heit, -schaft, -ung, -sal, -ing, -ling, -tum, -um, -ion, \
also -ität and its allomorphs attach -s- regularly. Acceptable linking elements: -s-.

Then, for a noun pair like Erbschaft + Steuer ranking 1-2 would produce Erbschaft+steuer,
and ranking 2-1 would produce Erbschaft+s+steuer.

I am learning German and starting the topic of compounds. \
I don't understand how these rules are ranked, and I need your help \
in my training to resolve such conflicts. To do so, we will play a game. \
Below is a set of rules that ALL apply to the same noun. Your task is:
1. Rank the rules correctly; given the lack of \
the context, focus the default order of these rules in German. \
2. Explain the principle that is used to rank the rules.
3. Guess what noun I have in mind.
You have a limited time to answer, so don't think much and answer directly what you believe is correct.

The rules are:
{constraints_str}
"""


CLASS_RANKING_PROMPT = """\
German compounds created from two nouns sometimes insert a so-called \
linking element in between, for example, Blume + Topf = Blume+n+topf. \
The correct output is determined by a set of rules. The rules, however, \
may be in conflict, in which case a careful rule ranking is required; \
the top-ranked rule produces the output.

Scholars identified three strategies to resolve rule conflicts. \
By the first strategy, the most regular rule wins the conflict. \
The most regular rule is defined as a rule that has the least exceptions. \
By the second strategy, the coverage (empirical) specificity plays decisive role. \
By coverage specificity is understood the number of compounds \
to which the rule is applicable; the less covered compounds, the more specific \
the rule. Finally, the condition specificity has been suggested. \
By this strategy, the rule that is more specific in its applicability condition \
takes precedence over more general rules.

I am now investigating the relative preference for these strategies by \
different scholars. To simplify the investigation, I want you to classify \
the claims I encounter, by these three strategies.

Below is a fragment to classify. Return strictly one label that classifies \
the scholar's strategy: "reg" for regularity, "cvg" for coverage (empirical) \
specificity, "cond" for condition specificity. Do not return anything else, \
only one singe label.

Fragment: {principle}
"""