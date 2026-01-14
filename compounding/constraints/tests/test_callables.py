import unittest

from compounding.constraints.data_utils.gecodb_compound_parser import Compound
from compounding.constraints.check_applicabilities import *


class CompoundingConstraintsCallablesZeroDefault(unittest.TestCase):
    
    # zero_default
    # The majority of compounds have a zero linker.
    
    def test_zero_default_is_applicable_0(self):
        compound = Compound("land_kreis")
        self.assertTrue(
            zero_default_is_applicable(compound)
        )

    def test_zero_default_applies_0(self):
        compound = Compound("land_kreis")
        self.assertTrue(
            zero_default_applies(compound)
        )

    
    def test_zero_default_is_applicable_1(self):
        compound = Compound("haus_tür")
        self.assertTrue(
            zero_default_is_applicable(compound)
        )

    def test_zero_default_applies_1(self):
        compound = Compound("haus_tür")
        self.assertTrue(
            zero_default_applies(compound)
        )


    def test_zero_default_is_applicable_2(self):
        compound = Compound("stadt_mauer")
        self.assertTrue(
            zero_default_is_applicable(compound)
        )

    def test_zero_default_applies_2(self):
        compound = Compound("stadt_mauer")
        self.assertTrue(
            zero_default_applies(compound)
        )


    def test_vzero_default_is_applicable_3(self):
        compound = Compound("land_+es_regierung")
        self.assertTrue(
            zero_default_is_applicable(compound)
        )

    def test_zero_default_applies_3(self):
        compound = Compound("land_+es_regierung")
        self.assertFalse(
            zero_default_applies(compound)
        )


    def test_zero_default_is_applicable_4(self):
        compound = Compound("haus_+=er_block")
        self.assertTrue(
            zero_default_is_applicable(compound)
        )

    def test_zero_default_applies_4(self):
        compound = Compound("haus_+=er_block")
        self.assertFalse(
            zero_default_applies(compound)
        )


    def test_zero_default_is_applicable_5(self):
        compound = Compound("stadt_+=e_tag")
        self.assertTrue(
            zero_default_is_applicable(compound)
        )

    def test_zero_default_applies_5(self):
        compound = Compound("stadt_+=e_tag")
        self.assertFalse(
            zero_default_applies(compound)
        )


if __name__ == '__main__':
    unittest.main()