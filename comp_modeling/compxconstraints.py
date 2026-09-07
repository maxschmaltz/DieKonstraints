import re
import pandas as pd
import yaml
from collections import defaultdict
from typing import Optional, Literal

from data_utils.gecodb_compound_parser import Compound
from check_applicability import l2p_satisfaction_checkers

constr_path = "constraints/constraints_all_revised.yaml"
# load constraints
with open(constr_path, encoding="utf-8") as f:
    yamls = list(yaml.safe_load_all(f))
    constraints: dict = yamls[-1]["constraints"]
    data_specs: dict = yamls[-2]["datasets"]

DNAME = "gecodb_v07_gn"


class CompXConstraints:

    def __init__(self, appl_row: pd.Series, dname: Optional[str]=DNAME):
        # input params
        self.appl_row = appl_row
        self.dname = dname
        # comp
        self.comp_gecodb = appl_row.name
        self.comp = Compound(appl_row.name)
        self.true = self._esc(self.comp.linkers[0].gecodb)
        # acceptable (P2L-generated) linkers
        self.acceptable_linkers = defaultdict(list)
        # add the default constraint right away
        def_id = "def-0"
        def_constr = constraints[def_id]
        self.acceptable_linkers["_"].append({
            "c_id": def_id,
            "confidence": self._reg(def_constr),
            "cvg": self._cvg(def_constr)
        })
        # unacceptable (L2P-restricted) linkers
        self.unacceptable_linkers = defaultdict(list)
        self._apply_constraints()

    def _esc(self, linker_gecodb: str) -> str:
        # remove allomorphy: it is regular and irrelevant
        # when predicting the linker;
        # -(")er- is merged in the constraint file already
        # NB! but not in the applicability indices
        return re.sub(r"_\+n", "_+en", linker_gecodb)

    def _reg(self, constr: dict) -> float:
        return constr["measures"][self.dname]["regularity"]["item"]

    def _cvg(self, constr: dict) -> float:
        return constr["measures"][self.dname]["coverage"]["item"]

    def _apply_constraints(self) -> None:

        for c_id, constr in constraints.items():

            if f"{c_id}_is_applicable" not in self.appl_row.index:
                continue

            # retrieve acceptable constraint linkers
            # (will become unacceptable for the L2P constraints)
            constr_linkers = list(set(
                [
                    self._esc(linker)
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
        constr_cooperation: bool,
        restrict_with_l2p: bool
    ):
        if method == "albright_hayes":
            return self._albright_hayes(
                constr_cooperation=constr_cooperation,
                restrict_with_l2p=restrict_with_l2p
            )

    def _albright_hayes(
        self,
        constr_cooperation: bool,
        restrict_with_l2p: bool
    ):
        
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
                    "cvg": most_conf_constr["cvg"]
                }
            else:
                # sum all the confidences
                confidence, cvg = 0, 0
                for constr in constrs:
                    confidence += constr["confidence"]
                    # the problem with coverage is that
                    # we cannot control for overlap here,
                    # so we just have to be mindful of that
                    cvg += constr["cvg"]
                linker_scoreboard[linker] = {
                    "confidence": confidence,
                    "cvg": cvg
                }

        if restrict_with_l2p:
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
                else:
                    # sum all the confidences
                    confidence, cvg = 0, 0
                    for constr in constrs:
                        confidence += constr["confidence"]
                        cvg += constr["cvg"]
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
                    # remove
                    linker_scoreboard.pop(linker)

        # indirectly following Albright & Hayes 2002,
        # prioritize the constraints with the higher coverage in case
        # regularity is the same
        self.linker_scoreboard = pd.DataFrame(linker_scoreboard).T  \
            .sort_values(by=["confidence", "cvg"], ascending=[False, False])

        # return generations: all linkers with the maximal confidence
        max_conf = self.linker_scoreboard["confidence"].max()
        max_linkers = self.linker_scoreboard[self.linker_scoreboard["confidence"] == max_conf]
        max_cvg = max_linkers["cvg"].max()
        preds = max_linkers[max_linkers["cvg"] == max_cvg]

        self.preds = preds.index.tolist()
        self.pred_conf = max_conf
        self.pred_cvg = max_cvg

        return self.preds