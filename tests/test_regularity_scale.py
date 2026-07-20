import unittest

from check_applicability.regularity_scale import REGULARITY_SCALE


class TestRegularityScale(unittest.TestCase):

    def test_supported_0(self):
        quantifier = "majority"
        reg_item = 0.578
        cvg_item = 1.0
        support_level = REGULARITY_SCALE.get_support_level(
            quantifier, reg_item, cvg_item
        )
        self.assertEqual(support_level, "supported")
        self.assertNotEqual(support_level, "supported+")
        self.assertNotEqual(support_level, "partially supported")
        self.assertNotEqual(support_level, "not supported")

    def test_supported_1(self):
        quantifier = "tendency"
        reg_item = 0.641
        cvg_item = 0.159
        support_level = REGULARITY_SCALE.get_support_level(
            quantifier, reg_item, cvg_item
        )
        self.assertEqual(support_level, "supported")
        self.assertNotEqual(support_level, "supported+")
        self.assertNotEqual(support_level, "partially supported")
        self.assertNotEqual(support_level, "not supported")

    def test_supported_2(self):
        quantifier = "usually"
        reg_item = 0.95
        cvg_item = 0.03
        support_level = REGULARITY_SCALE.get_support_level(
            quantifier, reg_item, cvg_item
        )
        self.assertEqual(support_level, "supported")
        self.assertNotEqual(support_level, "supported+")
        self.assertNotEqual(support_level, "partially supported")
        self.assertNotEqual(support_level, "not supported")

    def test_supported_3(self):
        quantifier = "regularly"
        reg_item = 0.98
        cvg_item = 0.215
        support_level = REGULARITY_SCALE.get_support_level(
            quantifier, reg_item, cvg_item
        )
        self.assertEqual(support_level, "supported")
        self.assertNotEqual(support_level, "supported+")
        self.assertNotEqual(support_level, "partially supported")
        self.assertNotEqual(support_level, "not supported")

    def test_supported_4(self):
        quantifier = "always"
        reg_item = 0.97
        cvg_item = 0.009
        support_level = REGULARITY_SCALE.get_support_level(
            quantifier, reg_item, cvg_item
        )
        self.assertEqual(support_level, "supported")
        self.assertNotEqual(support_level, "supported+")
        self.assertNotEqual(support_level, "partially supported")
        self.assertNotEqual(support_level, "not supported")


    def test_supported_plus_0(self):
        quantifier = "mostly"
        reg_item = 0.97
        cvg_item = 0.083
        support_level = REGULARITY_SCALE.get_support_level(
            quantifier, reg_item, cvg_item
        )
        self.assertEqual(support_level, "supported+")
        self.assertNotEqual(support_level, "supported")
        self.assertNotEqual(support_level, "partially supported")
        self.assertNotEqual(support_level, "not supported")

    def test_supported_plus_1(self):
        quantifier = "almost always"
        reg_item = 0.997
        cvg_item = 0.013
        support_level = REGULARITY_SCALE.get_support_level(
            quantifier, reg_item, cvg_item
        )
        self.assertEqual(support_level, "supported+")
        self.assertNotEqual(support_level, "supported")
        self.assertNotEqual(support_level, "partially supported")
        self.assertNotEqual(support_level, "not supported")


    def test_partially_supported_0(self):
        quantifier = "often"
        reg_item = 0.505
        cvg_item = 0.013
        support_level = REGULARITY_SCALE.get_support_level(
            quantifier, reg_item, cvg_item
        )
        self.assertEqual(support_level, "partially supported")
        self.assertNotEqual(support_level, "supported+")
        self.assertNotEqual(support_level, "supported")
        self.assertNotEqual(support_level, "not supported")

    def test_partially_supported_1(self):
        quantifier = "always"
        reg_item = 0.968
        cvg_item = 0.041
        support_level = REGULARITY_SCALE.get_support_level(
            quantifier, reg_item, cvg_item
        )
        self.assertEqual(support_level, "partially supported")
        self.assertNotEqual(support_level, "supported+")
        self.assertNotEqual(support_level, "supported")
        self.assertNotEqual(support_level, "not supported")


    def test_not_supported_0(self):
        quantifier = "regularly"
        reg_item = 0.747
        cvg_item = 0.007
        support_level = REGULARITY_SCALE.get_support_level(
            quantifier, reg_item, cvg_item
        )
        self.assertEqual(support_level, "not supported")
        self.assertNotEqual(support_level, "supported+")
        self.assertNotEqual(support_level, "supported")
        self.assertNotEqual(support_level, "partially supported")

    def test_not_supported_1(self):
        quantifier = "tend"
        reg_item = 0.146
        cvg_item = 0.455
        support_level = REGULARITY_SCALE.get_support_level(
            quantifier, reg_item, cvg_item
        )
        self.assertEqual(support_level, "not supported")
        self.assertNotEqual(support_level, "supported+")
        self.assertNotEqual(support_level, "supported")
        self.assertNotEqual(support_level, "partially supported")


    def test_incorrect_key_0(self):
        quantifier = "frequently"
        reg_item = 0.641
        cvg_item = 0.159
        with self.assertRaises(KeyError):
            _ = REGULARITY_SCALE.get_support_level(
                quantifier, reg_item, cvg_item
            )

    def test_incorrect_key_1(self):
        quantifier = "never"
        reg_item = 0.641
        cvg_item = 0.159
        with self.assertRaises(KeyError):
            _ = REGULARITY_SCALE.get_support_level(
                quantifier, reg_item, cvg_item
            )


if __name__ == '__main__':
    unittest.main()