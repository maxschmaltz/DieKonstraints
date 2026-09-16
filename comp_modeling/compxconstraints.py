import os
import re
import pandas as pd
from collections import defaultdict
from typing import Literal, List

from data_utils.gecodb_compound_parser import Compound
from data_utils.load_datasets import load_tsv_generic, load_constraints
from check_applicability import l2p_satisfaction_checkers

constr_dir = "constraints"
constraints = load_constraints(
    os.path.join(constr_dir, "constraints_all_revised.yaml")
)
constr_confidences = load_tsv_generic(
    os.path.join(constr_dir, "constr_confidences.tsv")
)

DEF_ID = "def-0"


class CompXConstraints:

    def __init__(
        self,
        appl_row: pd.Series
    ):
        # input params
        self.appl_row = appl_row
        # comp
        self.comp_gecodb = appl_row.name
        self.comp = Compound(appl_row.name)
        self.true = self.esc(self.comp.linkers[0].gecodb)
        # acceptable (P2L-generated) linkers
        self.acceptable_linkers = defaultdict(list)
        # add the default constraint into the competition
        self.acceptable_linkers["_"].append(DEF_ID)
        # unacceptable (L2P-restricted) linkers
        self.unacceptable_linkers = defaultdict(list)
        # helper for prediction
        self._conf_coeffs = {}
        self._apply_constraints()

    @staticmethod
    def esc(linker_gecodb: str) -> str:
        # remove allomorphy: it is regular and irrelevant
        # when predicting the linker;
        # -(")er- is merged in the constraint file already
        # NB! but not in the applicability indices
        linker_gecodb = re.sub(r"_\+n", "_+en", linker_gecodb)
        linker_gecodb = re.sub(r"_\+er", "_+=er", linker_gecodb)
        return linker_gecodb

    @staticmethod
    def esc_batch(linkers_gecodb: List[str]) -> List[str]:
        return list(set([CompXConstraints.esc(linker) for linker in linkers_gecodb]))

    def _apply_constraints(self) -> None:

        for c_id, constr in constraints.items():

            if f"{c_id}_is_applicable" not in self.appl_row.index:
                continue

            # retrieve acceptable constraint linkers
            # (will become unacceptable for the L2P constraints)
            constr_linkers = self.esc_batch(constr["acceptable_linkers"].copy())

            # if a constraint produces several linkers, only
            # distribute the confidence score between them
            self._conf_coeffs[c_id] = 1 / len(constr_linkers)

            # P2L: "generative" constraints that contribute 
            # to the acceptable linkers
            if c_id.startswith("p2l:"):
                if self.appl_row.get(f"{c_id}_is_applicable", False):
                    for linker in constr_linkers:
                        self.acceptable_linkers[linker].append(c_id)

            # unacceptable linkers: restricted by the L2P constraints;
            # here, we stick to a similar logic that the original L2P checks 
            # implemented, but now, since we are not validating actual linkers
            # but restrict potential linkers, we disregard the former
            elif c_id.startswith("l2p:"):

                if c_id == "l2p:en|non_par_m":
                    # special case: this constraint removes a restriction
                    # so it becomes a kind of a "generative" constraint;
                    # on the other hand, it does not prohibit _+en_
                    # if the conditions are not met
                    if (
                        l2p_satisfaction_checkers.en_non_par_m_is_presatisfied(self.comp) and
                        l2p_satisfaction_checkers.en_non_par_m_is_satisfied(self.comp)
                    ):
                        self.acceptable_linkers[linker].append(c_id)
                    continue

                is_presat_func = getattr(
                    l2p_satisfaction_checkers,
                    f"{constr["func_alias"]}_is_presatisfied",
                    lambda _: False # False if not implemented
                )
                # this check is required for some L2P linkers
                # that impose not general but targeted restrictions;
                # for example, there are some restrictions on
                # simplex nouns that may attach -s-, which leaves
                # complex nouns undefined with regard to this linker;
                # in order to not mark complex nouns in this example
                # as false negative (as if they cannot attach -s-
                # since they are not simplex), we run this additional check
                if not is_presat_func(self.comp):
                    continue

                is_sat_func = getattr(
                    l2p_satisfaction_checkers,
                    f"{constr["func_alias"]}_is_satisfied"
                )
                if not is_sat_func(self.comp):
                    # the condition that would allow the corresponding
                    # linker are not satisfied => the linker may not
                    # appear with this N1; e.g. 'Hund' would violate
                    # the er-paradigmaticity condition, and so
                    # -(")er- would be prohibited to appear with this N1
                    for linker in constr_linkers:
                        self.unacceptable_linkers[linker].append(c_id)

    def _build_linker_scoreboard(
            self,
            un_acceptable_linkers: dict
        ) -> pd.DataFrame:
        # sort linkers by the confidence
        linker_scoreboard = []
        for linker, c_ids in un_acceptable_linkers.items():
            for c_id in c_ids:
                if (not self.count_def_constr) and c_id == DEF_ID:
                    continue
                linker_scoreboard.append({
                    "linker": linker,
                    "c_id": c_id,
                    # # that's the most important property:
                    # # rank in the table in accordance with
                    # # the target property
                    # "constr_rank": self._constr_rank(c_id),
                    # for info
                    **(d := constr_confidences.loc[c_id].to_dict()),
                    # if a constraint produces several linkers, only
                    # take the average of the confidence score
                    "confidence": d[self._target] * self._conf_coeffs[c_id]
                })
        return pd.DataFrame(linker_scoreboard)#.sort_values(**self._sort_kwargs)

    def _agg_linker_scoreboard(self, linker_scoreboard: pd.DataFrame) -> pd.DataFrame:
        if self.constr_cooperation:
            # sum up the confidence and store the participating
            # constraints for the reference
            agg_map = {
                # limitation: coverages may overlap
                col: sum
                for col in self._sort_kwargs["by"]
            }
            agg_map["c_id"] = list
            # this will return the sum of target and auxiliary prop
            # for each linker, and a liststr of the contributing constraints
            linker_scoreboard = linker_scoreboard.groupby(
                "linker", as_index=False
            ).agg(agg_map).sort_values(**self._sort_kwargs)
            linker_scoreboard["c_id"] = linker_scoreboard["c_id"].map(
                lambda c_ids: ", ".join(c_ids)
            )
        else:
            # max pooling; this will keep only one row
            # per each linker where it achieves the highest confidence
            linker_scoreboard = linker_scoreboard   \
                .sort_values(**self._sort_kwargs)   \
                .drop_duplicates("linker", keep="first")
            linker_scoreboard = linker_scoreboard[
                # by = confidence + auxiliary property
                ["linker", *self._sort_kwargs["by"], "c_id"]
            ]
        linker_scoreboard.set_index("linker", inplace=True)
        return linker_scoreboard

    def predict(
        self,
        *,
        method: Literal["albright-hayes", "yang-cond", "yang-cvg"],
        count_def_constr: bool,
        constr_cooperation: bool,
        eliminate_with_l2p: bool
    ):

        self.method = method
        self.count_def_constr = count_def_constr
        self.constr_cooperation = constr_cooperation
        self.eliminate_with_l2p = eliminate_with_l2p

        # While the Elsewhere condition prescripts to stop generation
        # once an applicable rule is found, we adopt the workflow
        # of Albright & Hayes 2002. While iteration over the whole set
        # of rules is not characteristic to the Elsewhere condition,
        # the final prediction will be the one predicted by the 
        # highest-confident applicable constraint, which is exactly
        # what the Elsewhere condition does. So the real difference
        # is, really, not the prediction itself but how much information 
        # is elicited during the modeling, where Albright & Hayes 2002
        # clearly have an edge. Otherwise, the two are not rivals
        # but the same method, just with a different rule ordering.
        #
        # So what we do during prediction is:
        # 1. Sort the applicable constraints in the appropriate to the
        # method manner.
        # 2. Iterate over each constraint and record its prediction
        # and the associated confidence (Albright & Hayes 2002).
        # 3. Eliminate predictions restricted by the L2P constraints.
        # 4. Declare the most confident remaining outcome the prediction.

        # to resolve constraint conflicts, we will be referencing
        # the constraint confidence table prepared in advance,
        # see `data_utils/get_constr_confidences.py`;
        #
        # * there are a few records with all the records
        # (spec_score, cvg, reg) being equal; however, they
        # all are constraints on paradigmatic linkers,
        # so there should not be conflicts between those
        match method:
            case "albright-hayes":
                # use regularity as the confidence score;
                # in case of equal regularity, prefer constraints
                # with higher coverage, since high regularity
                # over a larger sample of compounds
                # is more reliable
                target = "reg"
                by = [target, "cvg"]
                ascend = [False, False]
            case "yang-cond":
                # use the specificity of the linguistic conditions
                # on constraint's potential applicability as its
                # confidence score; we developed a custom system
                # to evaluate the condition specificity,
                # see `data_utils/get_constr_confidences.py`;
                # on the contrary to Albright & Bayes 2002,
                # specificity prefers lower coverage, which
                # will be used to resolve conflicts of constraints
                # with equal condition specificity
                target = "spec_score"
                by = [target, "cvg"]
                ascend = [False, True]
            case "yang-cvg":
                # use the coverage score as the specificity 
                # of a constraint and its confidence score;
                # in case of equal coverage, resolve the conflict
                # by regularity
                target = "cvg"
                by = [target, "reg"]
                ascend = [True, False]
        # UPD: this step is not necessary, since we will adjust the
        # final confidence values to account for "multi-linker" constraints;
        # we keep it here because it is nice
        constr_confidences.sort_values(by=by, ascending=ascend, inplace=True)

        self._target = target
        # we unify sorting of the final scoreboard; we will sort it by
        # confidence, and values that have the same confidence score
        # will be sorted by an auxiliary property (cvg, reg, etc.)
        # in accordance with the method of prediction
        by[0] = "confidence"
        self._sort_kwargs = {"by": by, "ascending": ascend}

        # sort acceptable linkers by the confidence
        linker_scoreboard = self._build_linker_scoreboard(self.acceptable_linkers)

        if not linker_scoreboard.empty:
            # save for the record
            self.gen_constr_df = linker_scoreboard  \
                .sort_values(**self._sort_kwargs)   \
                .set_index("c_id")
            # aggregate under cooperation if necessary
            # and sort to produce the final ranking
            linker_scoreboard = self._agg_linker_scoreboard(linker_scoreboard)
        else:   # if only def was present and we ignore it
            # empty scoreboard; keep the structure to unify the 
            # L2P restriction workflow below
            linker_scoreboard = pd.DataFrame(
                {k: [] for k in ["linker", *self._sort_kwargs["by"], "c_id"]}
            ).set_index("linker")
            # empty df
            self.gen_constr_df = pd.DataFrame()

        if eliminate_with_l2p:

            linker_scoreboard["removed_by"] = ""
            
            # do all the same operations with the L2P constraint first
            # sort acceptable linkers by the confidence;
            # this df cannot be empty since there will be at least
            # a few paradigmatic restrictions
            linker_scoreboard_l2p = self._build_linker_scoreboard(self.unacceptable_linkers)
            # save for the record
            self.restr_constr_df = linker_scoreboard_l2p  \
                .sort_values(**self._sort_kwargs)   \
                .set_index("c_id")
            # aggregate under cooperation if necessary
            # and sort to produce the final restrictive ranking
            linker_scoreboard_l2p = self._agg_linker_scoreboard(linker_scoreboard_l2p)
            
            # now, remove linkers that are not acceptable
            # in accordance with the L2P constraints
            # if their confidence is higher
            for _, l2p_row in linker_scoreboard_l2p.iterrows():
                linker = l2p_row.name
                if not linker in linker_scoreboard.index:
                    continue
                gen_confidence = linker_scoreboard.loc[linker, "confidence"]
                # TODO: if the confidence is equal
                if l2p_row["confidence"] > gen_confidence:
                    # log removal
                    linker_scoreboard.loc[linker, "removed_by"] = l2p_row["c_id"]

        # record the final scoreboard
        self.linker_scoreboard = linker_scoreboard.copy()

        # return pred
        # remove the eliminated linker from the working scoreboard
        if eliminate_with_l2p:
            linker_scoreboard = linker_scoreboard[
                linker_scoreboard["removed_by"] == ""
            ]
        # if all the linkers were eliminated, use the default linker as a backup
        if linker_scoreboard.empty:
            self.pred_row = pd.Series(index=linker_scoreboard.columns)  # NAs
            self.y_pred = "_"
        else:
            self.pred_row = linker_scoreboard.iloc[0]   # will be empty if using default
            self.y_pred = self.pred_row.name

        return self.y_pred

    def update_pred_params(self, **update):
        # for demonstration purposes
        if not update:
            return self.y_pred
        kwargs = {
            "method": self.method,
            "count_def_constr": self.count_def_constr,
            "constr_cooperation": self.constr_cooperation,
            "eliminate_with_l2p": self.eliminate_with_l2p
        }
        kwargs.update(update)
        return self.predict(**kwargs)