import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RegularityLevel:

    name: str
    rank: int
    quantifiers: List[str]
    min_reg_item: float
    max_reg_item: float = field(default=1.01) # <


class RegularityScale:

    def __init__(self):

        # populate the scale
        self.scale = [
            
            RegularityLevel(
                "low_regularity",
                rank=1,
                min_reg_item=0.5,
                max_reg_item=0.6,
                quantifiers=[
                    "irregularly", "majority", "may",
                    "most", "mostly", "sometimes"
                ]
            ),

            RegularityLevel(
                "moderate_regularity",
                rank=2,
                min_reg_item=0.6,
                # natural cut-off is 0.8, there are only three constraints
                # with item reg in [0.8, 0.95)
                max_reg_item=0.95,
                quantifiers=[
                    "many", "more likely", "often",
                    "prefer", "tend", "tendency"
                ]
            ),

            RegularityLevel(
                "high_regularity",
                rank=3,
                min_reg_item=0.95,
                quantifiers=[
                    "almost all", "almost always",
                    "almost regularly", "usually"
                ]
            )

        ]

        self.quantifier_map = {}
        for reg_level in self.scale:
            for quantifier in reg_level.quantifiers:
                self.quantifier_map[quantifier] = reg_level

        # special case: regular
        for quantifier in ["all", "always", "regularly"]:
            self.quantifier_map[quantifier] = "regular"

    def _yang_theta(self, N: int) -> int:
        return N / np.log(N)

    def _tolerance_principle(self, N: int, e: int) -> bool:
        # the Tolerance Principle, Yang 2016;
        # if the number of exceptions to a rule is
        # n exc <= N / ln(N), the rule falls apart
        return e <= round(self._yang_theta(N))

    def _irreg_tolerance(self, N: int) -> int:
        return 1 / self._yang_theta(N)

    def _irreg_tolerance_principle(self, N: int, reg: float) -> bool:
        return reg >= (1 - self._irreg_tolerance(N))

    def _reg_level_by_quant(self, quantifier: str) -> RegularityLevel:
        return self.quantifier_map[quantifier]
    
    def _reg_level_by_reg(self, reg_item: float) -> RegularityLevel:
        for reg_level in self.scale:
            if (
                (reg_item >= reg_level.min_reg_item) &
                (reg_item < reg_level.max_reg_item)
            ):
                return reg_level
            
    def get_support_level(
        self,
        quantifier: str,
        reg_item: float,
        cvg_item_abs: int,
        n_violations: int
    ) -> str:

        # not confirmed constraint
        if reg_item < 0.5:
            return False, False, "not supported"

        # test the regularity by the Tolerance Principle
        is_productive = self._tolerance_principle(
            N=cvg_item_abs,
            e=n_violations
        )

        is_regular = self._irreg_tolerance_principle(
            N=cvg_item_abs,
            reg=reg_item
        )

        expected_reg_level = self._reg_level_by_quant(quantifier)
        actual_reg_level = self._reg_level_by_reg(reg_item)

        # even if the item reg very high, the constraint is not fully supported
        # until is_regular since the expected rank is beyond the scale then
        expected_rank = len(self.scale) + 1 if expected_reg_level == "regular" else expected_reg_level.rank
        actual_rank = len(self.scale) + 1 if is_regular else actual_reg_level.rank

        diff = actual_rank - expected_rank
        # (Shmalts 2026, 21)
        if diff >= 1:
            verdict = "supported+"
        elif diff == 0:
            verdict = "supported"
        elif diff == -1:
            verdict = "partially supported"
        else:
            verdict = "not supported"

        return is_productive, is_regular, verdict
        

REGULARITY_SCALE = RegularityScale()


quantifier = "almost always"
reg_item = 0.96
cvg_item_abs = 50
n_violations = 2
is_productive, is_regular, support_level = REGULARITY_SCALE.get_support_level(
    quantifier, reg_item, cvg_item_abs, n_violations
)