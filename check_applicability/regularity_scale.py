from dataclasses import dataclass
from typing import List


@dataclass
class RegularityLevel:

    name: str
    rank: int
    min_reg_item: float
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
        self.scale: List[RegularityLevel] = [None] * 4

        self.scale[0] = RegularityLevel(
            "low_regularity",
            rank=0,
            min_reg_item=0.5,
            max_reg_item=0.6,
            quantifiers=[
                Quantifier(value, None)
                for value in [
                    "irregularly", "majority", "may",
                    "most", "mostly", "sometimes"
                ]
            ]
        )

        self.scale[1] = RegularityLevel(
            "moderate_regularity",
            rank=1,
            min_reg_item=0.6,
            max_reg_item=0.9,
            quantifiers=[
                Quantifier(value, None)
                for value in [
                    "many", "more likely", "often",
                    "prefer", "tend", "tendency"
                ]
            ]
        )

        self.scale[2] = RegularityLevel(
            "increased_regularity",
            rank=2,
            min_reg_item=0.9,
            max_reg_item=0.98,
            quantifiers=[
                Quantifier(value, None)
                for value in [
                    "almost all", "almost always",
                    "almost regularly", "usually"
                ]
            ]
        )

        self.scale[3] = RegularityLevel(
            "high_regularity",
            rank=3,
            min_reg_item=0.98,
            max_reg_item=1.01,  # <, not <= is used
            quantifiers=[
                Quantifier(value, None)
                for value in [
                    "all", "always", "regularly"
                ]
            ]
        )

        self.quantifier_map = {}
        for reg_level in self.scale:
            for quantifier in reg_level.quantifiers:
                self.quantifier_map[quantifier.value] = quantifier.reg_level

    def _reg_level_by_quant(self, quantifier: str) -> RegularityLevel:
        return self.quantifier_map[quantifier]
    
    def _reg_level_by_reg(self, reg_item: float) -> RegularityLevel:
        for reg_level in self.scale:
            if (
                (reg_item >= reg_level.min_reg_item) &
                (reg_item < reg_level.max_reg_item)
            ):
                return reg_level
            
    def get_support_level(self, quantifier: str, reg_item: float, cvg_item: float) -> str:
        # correction for low cvg (see footnote Shmalts 2026, 21)
        if (cvg_item <= 0.01) and (reg_item >= 0.97):
            reg_item = 0.98 # adjust to reach high reg
        expected_reg_level = self._reg_level_by_quant(quantifier)
        actual_reg_level = self._reg_level_by_reg(reg_item)
        if not actual_reg_level:
            return "not supported"  # below 0.5
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