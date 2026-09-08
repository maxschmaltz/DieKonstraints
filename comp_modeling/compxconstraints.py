import re
import pandas as pd
from collections import defaultdict
from typing import Literal

from data_utils.gecodb_compound_parser import Compound
from data_utils.load_datasets import load_constraints
from check_applicability import l2p_satisfaction_checkers

constr_path = "constraints/constraints_all_revised.yaml"
constraints = load_constraints(constr_path)

DEF_ID = "def-0"
DEF_CONSTR = constraints[DEF_ID]


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
        self._def = {
            "c_id": DEF_ID,
            "confidence": self._reg(DEF_CONSTR),
            "cvg": self._cvg(DEF_CONSTR)
        }
        self.acceptable_linkers["_"].append(self._def)
        # unacceptable (L2P-restricted) linkers
        self.unacceptable_linkers = defaultdict(list)
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

    def _reg(self, constr: dict) -> float:
        return constr["measures"]["regularity"]["item"]

    def _cvg(self, constr: dict) -> float:
        return constr["measures"]["coverage"]["item"]

    def _apply_constraints(self) -> None:

        for c_id, constr in constraints.items():

            if f"{c_id}_is_applicable" not in self.appl_row.index:
                continue

            # retrieve acceptable constraint linkers
            # (will become unacceptable for the L2P constraints)
            constr_linkers = list(set(
                [
                    self.esc(linker)
                    for linker in constr["acceptable_linkers"].copy()
                ]
            ))

            # P2L: "generative" constraints that contribute 
            # to the acceptable linkers
            if c_id.startswith("p2l:"):
                if self.appl_row.get(f"{c_id}_is_applicable", False):
                    for linker in constr_linkers:
                        self.acceptable_linkers[linker].append({
                            "c_id": c_id,
                            # divide by the number of the acceptable linkers
                            # to control for the predictive power;
                            # e.g. the fact that `p2l:decl_cl:pl:#er-0/er|def-0/er`
                            # (produces both _ and _+=er_) has an item regularity
                            # of 0.815 does not mean that either of these
                            # linkers appears at regularity 0.815 individually;
                            # the constraint contributes 0.815 to both linkers
                            # in sum, so each should receive only a half
                            "confidence": round(
                                self._reg(constr) / len(constr_linkers), 3
                            ),
                            "cvg": self._cvg(constr),
                        })

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
                        self.acceptable_linkers[linker].append({
                            "c_id": c_id,
                            "confidence": self._reg(constr),
                            "cvg": self._cvg(constr),
                        })
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
                        self.unacceptable_linkers[linker].append({
                            "c_id": c_id,
                            "confidence": self._reg(constr),
                            "cvg": self._cvg(constr),
                        })

    def predict(
        self,
        *,
        method: Literal["albright_hayes"],
        count_def_constr: bool,
        constr_cooperation: bool,
        restrict_with_l2p: bool
    ):
        if method == "albright_hayes":
            return self._albright_hayes(
                count_def_constr=count_def_constr,
                constr_cooperation=constr_cooperation,
                restrict_with_l2p=restrict_with_l2p
            )

    def _albright_hayes(
        self,
        count_def_constr: bool,
        constr_cooperation: bool,
        restrict_with_l2p: bool
    ):

        if (
            not count_def_constr and
            self._def in self.acceptable_linkers.get("_", [])
        ):
            # do not use in the calculation
            # of the prediction; only be used as a backup
            # in case no other linker could be predicted
            self.acceptable_linkers["_"].remove(self._def)
            # remove the linker from acceptable
            # if def was the only supporting constraint
            if not self.acceptable_linkers["_"]:
                self.acceptable_linkers.pop("_")
        
        # first, sort acceptable linkers by the confidence
        linker_scoreboard = {}
        for linker, constrs in self.acceptable_linkers.items():
            if not constr_cooperation:
                # original Albright & Bayes method:
                # take the max confidence score;
                # note that we are using the raw
                # confidence score, or regularity
                most_conf_constr = max(
                    constrs,
                    key=lambda x: x["confidence"]
                )
                linker_scoreboard[linker] = {
                    "confidence": most_conf_constr["confidence"],
                    "cvg": most_conf_constr["cvg"],
                    "constraints": most_conf_constr["c_id"]
                }
            else:
                # sum all the confidences
                confidence, cvg, c_ids = 0, 0, []
                for constr in constrs:
                    confidence += constr["confidence"]
                    # the problem with coverage is that
                    # we cannot control for overlap here,
                    # so we just have to be mindful of that
                    cvg += constr["cvg"]
                    c_ids.append(constr["c_id"])
                linker_scoreboard[linker] = {
                    "confidence": confidence,
                    "cvg": cvg,
                    "constraints": ", ".join(c_ids)
                }

        if restrict_with_l2p:
            linker_scoreboard_extended = linker_scoreboard.copy()
            # remove linkers that are not acceptable
            # in accordance with the L2P constraints
            self.l2p_removals = {}
            for linker, constrs in self.unacceptable_linkers.items():
                if not linker in linker_scoreboard:
                    continue
                if not constr_cooperation:
                    # original Albright & Bayes method:
                    # take the max confidence
                    most_conf_constr = max(
                        constrs,
                        key=lambda x: x["confidence"]
                    )
                    confidence = most_conf_constr["confidence"]
                    cvg = most_conf_constr["cvg"]
                    to_log = most_conf_constr
                    c_ids = [to_log["c_id"]]
                else:
                    # sum all the confidences
                    confidence, cvg, c_ids = 0, 0, []
                    for constr in constrs:
                        confidence += constr["confidence"]
                        cvg += constr["cvg"]
                        c_ids.append(constr["c_id"])
                    to_log = constrs
                # remove the linker only if the restrictive
                # L2P constraint(s) has (have) a higher confidence
                # than the P2L one(s); indirectly following Albright & Hayes 2002,
                # choose the constraints with the higher coverage in case
                # regularity is the same
                if (
                    confidence > linker_scoreboard[linker]["confidence"] or
                    (
                        confidence == linker_scoreboard[linker]["confidence"] and
                        cvg > linker_scoreboard[linker]["cvg"]
                    )
                ):
                    # log removal
                    self.l2p_removals[linker] = to_log
                    linker_scoreboard_extended[linker]["removed_by"] = ", ".join(c_ids)
                    # remove
                    linker_scoreboard.pop(linker)
                else:
                    linker_scoreboard_extended[linker]["removed_by"] = ""

        # if all the linkers were eliminated, use the default linker
        # as a backup
        if not linker_scoreboard:
            linker_scoreboard = {"_": self._def}

        if restrict_with_l2p and not linker_scoreboard_extended:
            linker_scoreboard_extended = {"_": {**self._def, "removed_by": ""}}

        # indirectly following Albright & Hayes 2002,
        # prioritize the constraints with the higher coverage in case
        # regularity is the same
        self.linker_scoreboard = pd.DataFrame(linker_scoreboard).T  \
            .sort_values(by=["confidence", "cvg"], ascending=[False, False])
        if restrict_with_l2p:
            self.linker_scoreboard_extended = pd.DataFrame(linker_scoreboard_extended).T  \
                .sort_values(by=["confidence", "cvg"], ascending=[False, False])

        # return generations; since we distribute the confidence
        # for the constraints that accept more than one linker,
        # the probability of several linkers to have both the same
        # confidence and regularity is virtually zero
        pred_row = self.linker_scoreboard.iloc[0]
        self.y_pred = pred_row.name
        self.pred_conf = pred_row["confidence"]
        self.pred_cvg = pred_row["cvg"]

        return self.y_pred