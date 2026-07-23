import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Union


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
                "low regularity",
                rank=1,
                min_reg_item=0.5,
                max_reg_item=0.6,
                quantifiers=[
                    "irregularly", "majority", "may",
                    "most", "mostly", "sometimes"
                ]
            ),

            RegularityLevel(
                "moderate regularity",
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
                "high regularity",
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

    def _tolerance_principle(self, N: int, e: Union[int, float]) -> bool:
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
        n_violations: float
    ) -> Tuple[bool, bool, str, str, str]:

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
        if expected_reg_level == "regular":
            expected_rank = len(self.scale) + 1
        else:
            expected_rank = expected_reg_level.rank
            expected_reg_level = expected_reg_level.name

        # not confirmed constraint
        if reg_item < 0.5:
            return (
                is_productive,
                is_regular,
                expected_reg_level,
                "below scale",
                "not supported"
            )

        if is_regular:
            actual_rank = len(self.scale) + 1
            actual_reg_level = "regular"
        else:
            actual_rank = actual_reg_level.rank
            actual_reg_level = actual_reg_level.name

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

        return (
            is_productive, is_regular,
            expected_reg_level, actual_reg_level,
            verdict
        )
        

REGULARITY_SCALE = RegularityScale()