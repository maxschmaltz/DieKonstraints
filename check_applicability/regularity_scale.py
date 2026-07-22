import numpy as np
from dataclasses import dataclass
from typing import List, Union
from types import FunctionType


@dataclass
class RegularityLevel:

    name: str
    rank: int
    min_reg_item: Union[float, FunctionType]
    max_reg_item: float
    quantifiers: List[str]  # -> List[Quantifier]

    def __post_init__(self):
        for q in self.quantifiers:
            q.reg_level = self


@dataclass
class Quantifier:
    value: str
    reg_level: RegularityLevel


class RegularityScale:

    def __init__(self):

        # populate the scale
        self.scale = [
            
            RegularityLevel(
                "low_regularity",
                rank=0,
                min_reg_item=0.5,
                max_reg_item=0.6,
                quantifiers=[
                    "irregularly", "majority", "may",
                    "most", "mostly", "sometimes"
                ]
            ),

            RegularityLevel(
                "moderate_regularity",
                rank=1,
                min_reg_item=0.6,
                max_reg_item=0.8,
                quantifiers=[
                    "many", "more likely", "often",
                    "prefer", "tend", "tendency"
                ]
            ),

            RegularityLevel(
                "increased_regularity",
                rank=2,
                min_reg_item=0.8,
                max_reg_item=0.95,
                quantifiers=[
                    "almost all", "almost always",
                    "almost regularly", "usually"
                ]
            ),

            RegularityLevel(
                "high_regularity",
                rank=3,
                min_reg_item=0.95,
                max_reg_item=0.98,
                quantifiers=["all", "always", "regularly"]
            ),

            RegularityLevel(
                "high_regularity",
                rank=4,
                min_reg_item=lambda N: 1 - (self._tp(N) - N),
                max_reg_item=1.01,  # <, not <= is used
                quantifiers=["all", "always", "regularly"]
            )

        ]

        self.quantifier_map = {}
        for reg_level in self.scale:
            for quantifier in reg_level.quantifiers:
                self.quantifier_map[quantifier.value] = quantifier.reg_level

    def _reg_level_by_quant(self, quantifier: str) -> RegularityLevel:
        return self.quantifier_map[quantifier]
    
    def _reg_level_by_reg(self, reg_item: float, cvg_item_abs: int) -> RegularityLevel:
        for reg_level in self.scale:
            min_reg_item = (
                reg_level.min_reg_item if isinstance(float, reg_level.min_reg_item)
                # run as function
                else reg_level.min_reg_item(cvg_item_abs)
            )
            if (
                (reg_item >= min_reg_item) &
                (reg_item < reg_level.max_reg_item)
            ):
                return reg_level
            
    def _tp(self, N: int) -> int:
        # the Tolerance Principle, Yang 2016
        return round(N / np.log(N))
            
    def get_support_level(
        self,
        quantifier: str,
        reg_item: float,
        cvg_item_abs: int
    ) -> str:
        if reg_item < 0.5:
            return "not supported"
        expected_reg_level = self._reg_level_by_quant(quantifier)
        actual_reg_level = self._reg_level_by_reg(reg_item, cvg_item_abs)
        diff = actual_reg_level.rank - expected_reg_level.rank
        # (Shmalts 2026, 21)
        if diff >= 1:
            return "supported+"
        elif diff == 0:
            return "supported"
        elif diff == -1:
            return "partially supported"
        else:
            return "not supported"
        

REGULARITY_SCALE = RegularityScale()