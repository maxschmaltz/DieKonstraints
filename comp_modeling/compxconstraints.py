import pandas as pd
import yaml
from collections import defaultdict

from data_utils.gecodb_compound_parser import Compound
from check_applicability import l2p_satisfaction_checkers

constr_path = "constraints/constraints_all_revised.yaml"
# load constraints
with open(constr_path, encoding="utf-8") as f:
    yamls = list(yaml.safe_load_all(f))
    constraints: dict = yamls[-1]["constraints"]
    data_specs: dict = yamls[-2]["datasets"]


class CompXConstraints:

    def __init__(self, appl_row: pd.Series, dname: str):
        # input params
        self.appl_row = appl_row
        self.dname = dname
        # comp
        self.comp_gecodb = appl_row.name
        self.comp = Compound(appl_row.name)
        self.true = self.comp.linkers[0].morph
        # acceptable (P2L-generated) linkers
        self.acceptable_linkers = defaultdict(list)
        # add the default constraint right away
        def_id = "def-0"
        def_constr = constraints[def_id]
        self.acceptable_linkers["_"].append({
            "c_id": def_id,
            "item_reg": self._reg(def_constr),
            "item_cvg": self._cvg(def_constr)
        })
        # unacceptable (L2P-restricted) linkers
        self.unacceptable_linkers = defaultdict(list)
        self._apply_constraints()

    def _reg(self, constr: dict) -> float:
        return constr["measures"][self.dname]["regularity"]["item"]

    def _cvg(self, constr: dict) -> float:
        return constr["measures"][self.dname]["coverage"]["item"]

    def _apply_constraints(self) -> None:

        for c_id, constr in constraints.items():

            # retrieve acceptable constraint linkers
            # (will become unacceptable for the L2P constraints)
            constr_linkers: list = constr["acceptable_linkers"].copy()
            # remove allomorphs; -(")er- is merged in the constraint file
            # NB! but not in the applicability indices
            for allo in ["_+n_", "_+ns_"]:
                if allo in constr_linkers:
                    constr_linkers.remove(allo)
                    constr_linkers.append(allo.replace("+n", "+en"))
            constr_linkers = list(set(constr_linkers))

            # P2L: "generative" constraints that contribute 
            # to the acceptable linkers
            if c_id.startswith("p2l:"):
                if self.appl_row.get(f"{c_id}_is_applicable", False):
                    for linker in constr_linkers:
                        self.acceptable_linkers[linker].append({
                            "c_id": c_id,
                            "item_reg": self._reg(constr),
                            "item_cvg": self._cvg(constr),
                        })

            # unacceptable linkers: restricted by the L2P constraints;
            # here, we stick to a similar logic that the original L2P checks 
            # implemented, but now, since we are not validating actual linkers
            # but restrict potential linkers, we disregard the former
            elif c_id.startswith("l2p:"):
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
                            "item_reg": self._reg(constr),
                            "item_cvg": self._cvg(constr),
                        })