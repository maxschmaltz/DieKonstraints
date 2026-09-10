import os
import re
import pandas as pd
from typing import List, Tuple, Union

from data_utils.load_datasets import load_constraints


# python3 -m data_utils.get_constr_confidences
def main():

    # When modeling compounding, we have two options as of
    # what to use as the confidence score to resolve constraint
    # conflicts:
    # * Regularity (Albright & Hayes 2002). While Albright & Hayes 2002
    # use type regularity as raw confidence and derive a final confidence
    # out of it by adding the absolute coverage into equation, we do not
    # replicate this step. TODO: add justification. We therefore use
    # item regularity instead.
    # * Specificity (Yang 2016, TODO). In accordance with the Elsewhere Condition,
    # the order of the rule application follows the decrease of generalization
    # specificity, starting with the most specific and finishing with the
    # most general (default) constraint. We define two variants of "specificity":
    # 1. Coverage specificity. Specificity is simply defined by the number
    # of the covered compounds: the more covered compounds, the less
    # specific the constraints.
    # 2. Condition specificity. Specificity of the constraint is defined by the
    # specificity of the linguistic conditions on its potential applicability.
    # This should take into account both the composition of the conditions,
    # and the specificity of each singular condition in its composition.
    # For example, [PL:e] is less specific than [PL:e] & [sem:PL],
    # whereas [coda:VO] is less specific than [coda:e].
    # * While further effects hold (stem frequency, rule frequency, etc.
    # see Yang 2016, we initially concentrate on these two as the baseline.
    #
    # In this script, we derive the specificity score of the constraints
    # by the definition specificity. For that, we create a custom
    # scoring system; details are given below. For convenience,
    # we also add the coverage and the regularity values in the same
    # table to be able to access them during modeling conveniently.

    constr_dir = "constraints"
    constraints = load_constraints(
        os.path.join(constr_dir, "constraints_all_revised.yaml")
    )

    # gather all unique conditions
    all_conditions = {
        c_id: constr["conditions"]
        for c_id, constr in constraints.items()
    }
    unique_conditions = list(set(all_conditions.values()))

    # extract singular conditions and parse the complex
    # conditions from those
    sing_cond_re = re.compile(r"\[\w+:[!a-zA-Z]+\]")
    comp_cond_re = re.compile(r"\[\d+( [&|] \d+){1,}\]")

    def _parse_condition(c: str, term_map: dict) -> Tuple[list, dict]:

        if not c:
            # def
            return [], term_map

        term_map_r = {k: v for v, k in term_map.items()}

        # in: '[PL:o] & [[[drv:smpx] & [G:!F]] | [G:F]]'
        #
        # first, extract all singular conditions
        # and replace them by terms
        #
        # out: '0 & [[1 & 2] | 3]'
        for condition in sing_cond_re.findall(c):
            v = condition[1:-1] # remove brackets
            if not v in term_map:
                i = len(term_map)
                term_map[v] = i
                term_map_r[i] = v
            else:
                i = term_map[v]
            c = c.replace(condition, str(i), count=1)

        # now, we can recursively merge the terms
        # until we are left with a single operation
        #
        # out: '0 & 5'
        while c.count("["):
            m = comp_cond_re.search(c).group(0)
            if not m in term_map:
                i = len(term_map)
                term_map[m] = i
                term_map_r[i] = m
            else:
                i = term_map[m]
            c = c.replace(m, str(i))

        # now, use the map to unparse the conditions back
        #
        # map:
        # {0: '[PL:o]',
        #  1: '[drv:smpx]',
        #  2: '[G:!F]',
        #  3: '[G:F]',
        #  4: '[1 & 2]',
        #  5: '[4 | 3]'}
        #
        # out: ['PL:o', (['drv:smpx', 'G:!F'], 'G:F')]
        def _parse_terms(terms: str) -> List[str]:
            if not re.search(r"\d", terms):
                # decoded
                return terms
            if "&" in terms:
                # remove brackets
                terms = re.sub(r"(^\[|\]$)", "", terms)
                terms = terms.split(" & ")
                return [
                    _parse_terms(term)
                    for term in terms
                ]
            elif "|" in terms:
                # remove brackets
                terms = re.sub(r"(^\[|\]$)", "", terms)
                terms = terms.split(" | ")
                return tuple([
                    _parse_terms(term)
                    for term in terms
                ])
            else:
                return _parse_terms(term_map_r[int(terms)])

        return _parse_terms(c), term_map

    # now our string conditions are parsed into
    # nested structures of singular condition strings;
    # the list conjuncts, and the tuple disjuncts conditions;
    # for example, '[PL:o] & [[[drv:smpx] & [G:!F]] | [G:F]]'
    # became ['PL:o', (['drv:smpx', 'G:!F'], 'G:F')]
    term_map = {}
    conditions_parsed = {}
    for condition in unique_conditions:
        parsed_condition, term_map = _parse_condition(condition, term_map)
        conditions_parsed[condition] = parsed_condition

    # Now we rank the complex conditions by their specificity.
    # We do that by deriving an aggregate specificity of the 
    # complex condition from the composition of the singular
    # conditions it consists of.
    #
    # One singular condition is worth a base score of 10 points.
    # On top of this base score, each singular condition
    # gets its own specificity score depending on how
    # general its condition is (more to less specific here):
    # 1. Specific values. They are encoded as lowercase values.
    # 2. Set(s) of values. They are encoded as uppercase values.
    # The longer the label, the more sets are included and the
    # less specific the resulting set. For instance,
    # coda:S means sibilant, coda:VO means vowel, and coda:CLR --
    # a set of clusters.
    # 3. Negations of sets of values. They are encoded as 
    # sets of values with a preceding exclamation mark.
    # Since longer set are less specific,
    # negation of a longer set is more specific.
    # 4. Negations of specific values. They are encoded as
    # specific values with a preceding exclamation mark.
    #
    # We agree that between-category comparisons are a bit shaky.
    # For example, is having a certain gender as specific as having
    # a certain plural form? One might argue that we can use some sort of
    # in-category value probability for a more accurate comparison;
    # in our example, P(gender=masc) > P(pl=e) so the former should
    # be less specific. However, for that we would need to know
    # all the possible outcomes of each category. This might
    # be not only inefficient, but also not always possible (semantics).
    # Besides, it is not clear then if we should include non-occurring
    # but existing values (certain suffixes of N1). While this direction
    # is worth exploring, we simplify the scoring for now and allow
    # for direct between-category comparisons.
    # 
    # Once we have the scores for each singular condition,
    # we can assemble the overall score of the complex condition
    # recursively. Conjunction of conditions is worth
    # the sum of the components. Disjunction of conditions is worth
    # the mean of the components.
    # For example, the default condition will have a (base) score of 0,
    # [coda:e] a (base) score of 1=, [[coda:CLT] | [[coda:CLT] & [drv:PRX']]
    # a (base) score of 15, [['G:!F'] & ['drv:smpx']] a (base) score of 20, etc.
    #
    # The conditions that still share the same rank after
    # in-category comparisons, we refer to their item coverage
    # to infer the least extensive, hence, more specific, constraint.

    def _spec_score(singular_condition: str) -> float:
        if singular_condition.startswith("!"):
            if singular_condition[1].isupper():
                # mark specificity of a set
                # while staying in the range of [3; 4]
                # longer are more specific
                l = len(singular_condition) - 1
                penalty = 4 - 0.1 * l
            else:
                penalty = 4
        else:
            if singular_condition[0].isupper():
                # mark specificity of a set
                # while staying in the range of [2; 3];
                # longer are less specific
                l = len(singular_condition)
                penalty = 2 + 0.1 * l
            else:
                penalty = 1
        # get a score in range [1; 4]
        return 5 - penalty

    def _score_condition(condition: Union[str, list, tuple]) -> float:
        if isinstance(condition, str):
            # singular condition: base score of 10 and
            # own specificity score
            base = 10
            # each singular score has a form of
            # cat:cond; we are scoring cond
            _, cond = condition.split(":")
            score = base + _spec_score(cond)
        elif isinstance(condition, list):
            # conjunction: sum
            score = sum([
                _score_condition(term)
                for term in condition
            ])
        elif isinstance(condition, tuple):
            # disjunction: mean
            score = sum([
                _score_condition(term)
                for term in condition
            ]) / len(condition)
        return round(score, 1)

    conditions_scored = {
        condition: _score_condition(parsed_condition)
        for condition, parsed_condition in conditions_parsed.items()
    }
    # sort by the score
    conditions_scored = {
        k: v for k, v in sorted(
            conditions_scored.items(),
            key=lambda x: x[1],
            reverse=True
        )
    }

    # '[PL:!en] & [G:N] & [nsyl:!mono] & [coda:CLT] & [loan:T] & [sem:PL]'	73.3
    # '[G:F] & [PL:en] & [coda:CN] & [sem:PL]'	                            52.5
    # '[G:F] & [PL:en] & [coda:CN] & [sem:!PL]'	                            50.9
    # ...
    # '[coda:VW]'	12.8
    # '[drv:PRX]'	12.7
    # '[coda:CLT]'	12.7
    # '[drv:SFX]'	12.7
    # ''            0.0
    conditions_scored_df = pd.DataFrame(
        {"spec_score": conditions_scored.values()},
        index=conditions_scored.keys()
    )

    # join the tables to map the constraints
    # to their specificities
    all_conditions_df = pd.DataFrame(
        {"c_id": all_conditions.keys()},
        index=all_conditions.values()
    )
    constr_specificity_df = all_conditions_df.join(
        conditions_scored_df,
        how="left"
    )
    constr_specificity_df = constr_specificity_df   \
        .reset_index(drop=False)    \
        .set_index("c_id")

    # add coverages to be able to ultimately resolve
    # constraints with the same scores,
    # and regularities for Albright & Hayes 2002
    measures = {
        c_id: {
            "cvg": (
                constr["measures"]["coverage"]["item"]
                # force the worst coverage rank for unimplemented
                # constraints; this step is, however,
                # optional, since such constraints
                # will not be used in modeling, anyway
                if constr["measures"] != "NA" else 2
            ),
            "reg": (
                constr["measures"]["regularity"]["item"]
                # same
                if constr["measures"] != "NA" else 0
            )
        }
        for c_id, constr in constraints.items()
    }
    coverages_df = pd.DataFrame(measures).T
    constr_specificity_df = constr_specificity_df.join(
        coverages_df,
        how="left"
    ).rename(columns={"index": "condition"})

    # final sorting: score (higher is better), cvg between 
    # identical scores (lower is better);
    # in principle, this is also optional, since the 
    # constraints are sorted by confidence dynamically 
    # for each individual compound
    constr_specificity_df = constr_specificity_df.sort_values(
        by=["spec_score", "cvg"],
        ascending=[False, True]
    )

    constr_specificity_df.to_csv(
        os.path.join(constr_dir, "constr_confidences.tsv"),
        sep="\t",
        header=True,
        index=True
    )


if __name__ == "__main__":
    main()