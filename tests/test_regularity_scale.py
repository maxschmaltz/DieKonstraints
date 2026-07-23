import unittest

from check_applicability.regularity_scale import REGULARITY_SCALE


class TestRegularityScale(unittest.TestCase):

    def test_tolerance_principle_0(self):
        # Yang 2016: 67
        N = 10
        e = 4
        self.assertTrue(REGULARITY_SCALE._tolerance_principle(N, e))
        self.assertFalse(REGULARITY_SCALE._tolerance_principle(N, e + 1))

    def test_tolerance_principle_1(self):
        # Yang 2016: 67
        N = 20
        e = 7
        self.assertTrue(REGULARITY_SCALE._tolerance_principle(N, e))
        self.assertFalse(REGULARITY_SCALE._tolerance_principle(N, e + 1))

    def test_tolerance_principle_2(self):
        # Yang 2016: 67
        N = 50
        e = 13
        self.assertTrue(REGULARITY_SCALE._tolerance_principle(N, e))
        self.assertFalse(REGULARITY_SCALE._tolerance_principle(N, e + 1))

    def test_tolerance_principle_3(self):
        # Yang 2016: 67
        N = 100
        # 23 seems like an error in the original table because
        # 100 / ln(100) ~= 21.715;
        # UPD: it should be 22 indeed, see Yang 2016: 62
        e = 22
        self.assertTrue(REGULARITY_SCALE._tolerance_principle(N, e))
        self.assertFalse(REGULARITY_SCALE._tolerance_principle(N, e + 1))

    def test_tolerance_principle_4(self):
        # Yang 2016: 67
        N = 200
        e = 38
        self.assertTrue(REGULARITY_SCALE._tolerance_principle(N, e))
        self.assertFalse(REGULARITY_SCALE._tolerance_principle(N, e + 1))

    def test_tolerance_principle_5(self):
        # Yang 2016: 67
        N = 500
        e = 80
        self.assertTrue(REGULARITY_SCALE._tolerance_principle(N, e))
        self.assertFalse(REGULARITY_SCALE._tolerance_principle(N, e + 1))

    def test_tolerance_principle_6(self):
        # Yang 2016: 67
        N = 1000
        e = 145
        self.assertTrue(REGULARITY_SCALE._tolerance_principle(N, e))
        self.assertFalse(REGULARITY_SCALE._tolerance_principle(N, e + 1))

    def test_tolerance_principle_7(self):
        # Yang 2016: 67
        N = 5000
        e = 587
        self.assertTrue(REGULARITY_SCALE._tolerance_principle(N, e))
        self.assertFalse(REGULARITY_SCALE._tolerance_principle(N, e + 1))


    def test_supported_0(self):
        quantifier = "majority"
        reg_item = 0.578
        cvg_item_abs = 275000
        n_violations = 115000
        is_productive, is_regular, support_level = REGULARITY_SCALE.get_support_level(
            quantifier, reg_item, cvg_item_abs, n_violations
        )
        self.assertFalse(is_productive)
        self.assertFalse(is_regular)
        self.assertEqual(support_level, "supported")

    def test_supported_1(self):
        quantifier = "tendency"
        reg_item = 0.641
        cvg_item_abs = 525
        n_violations = 180
        is_productive, is_regular, support_level = REGULARITY_SCALE.get_support_level(
            quantifier, reg_item, cvg_item_abs, n_violations
        )
        self.assertFalse(is_productive)
        self.assertFalse(is_regular)
        self.assertEqual(support_level, "supported")

    def test_supported_2(self):
        quantifier = "usually"
        reg_item = 0.95
        cvg_item_abs = 100
        n_violations = 5
        is_productive, is_regular, support_level = REGULARITY_SCALE.get_support_level(
            quantifier, reg_item, cvg_item_abs, n_violations
        )
        self.assertTrue(is_productive)
        self.assertFalse(is_regular)
        self.assertEqual(support_level, "supported")

    def test_supported_3(self):
        quantifier = "regularly"
        reg_item = 0.995
        cvg_item_abs = 750
        n_violations = 5
        is_productive, is_regular, support_level = REGULARITY_SCALE.get_support_level(
            quantifier, reg_item, cvg_item_abs, n_violations
        )
        self.assertTrue(is_productive)
        self.assertTrue(is_regular)
        self.assertEqual(support_level, "supported")

    def test_supported_4(self):
        quantifier = "always"
        reg_item = 0.96
        cvg_item_abs = 50
        n_violations = 2
        is_productive, is_regular, support_level = REGULARITY_SCALE.get_support_level(
            quantifier, reg_item, cvg_item_abs, n_violations
        )
        self.assertTrue(is_productive)
        self.assertTrue(is_regular)
        self.assertEqual(support_level, "supported")


    def test_supported_plus_0(self):
        quantifier = "almost always"
        reg_item = 0.96
        cvg_item_abs = 50
        n_violations = 2
        is_productive, is_regular, support_level = REGULARITY_SCALE.get_support_level(
            quantifier, reg_item, cvg_item_abs, n_violations
        )
        self.assertTrue(is_productive)
        self.assertTrue(is_regular)
        self.assertEqual(support_level, "supported+")

    def test_supported_plus_1(self):
        quantifier = "mostly"
        reg_item = 0.84
        cvg_item_abs = 500
        n_violations = 80
        is_productive, is_regular, support_level = REGULARITY_SCALE.get_support_level(
            quantifier, reg_item, cvg_item_abs, n_violations
        )
        self.assertTrue(is_productive)
        self.assertFalse(is_regular)
        self.assertEqual(support_level, "supported+")


    def test_partially_supported_0(self):
        quantifier = "often"
        reg_item = 0.505
        cvg_item_abs = 45
        n_violations = 22
        is_productive, is_regular, support_level = REGULARITY_SCALE.get_support_level(
            quantifier, reg_item, cvg_item_abs, n_violations
        )
        self.assertFalse(is_productive)
        self.assertFalse(is_regular)
        self.assertEqual(support_level, "partially supported")

    def test_partially_supported_1(self):
        quantifier = "always"
        reg_item = 0.98
        cvg_item_abs = 750
        n_violations = 15
        is_productive, is_regular, support_level = REGULARITY_SCALE.get_support_level(
            quantifier, reg_item, cvg_item_abs, n_violations
        )
        self.assertTrue(is_productive)
        self.assertFalse(is_regular)
        self.assertEqual(support_level, "partially supported")


    def test_not_supported_0(self):
        quantifier = "regularly"
        reg_item = 0.641
        cvg_item_abs = 525
        n_violations = 180
        is_productive, is_regular, support_level = REGULARITY_SCALE.get_support_level(
            quantifier, reg_item, cvg_item_abs, n_violations
        )
        self.assertFalse(is_productive)
        self.assertFalse(is_regular)
        self.assertEqual(support_level, "not supported")

    def test_not_supported_1(self):
        quantifier = "tend"
        reg_item = 0.146
        cvg_item_abs = 900
        n_violations = 770
        is_productive, is_regular, support_level = REGULARITY_SCALE.get_support_level(
            quantifier, reg_item, cvg_item_abs, n_violations
        )
        self.assertFalse(is_productive)
        self.assertFalse(is_regular)
        self.assertEqual(support_level, "not supported")


    def test_incorrect_key_0(self):
        quantifier = "frequently"
        with self.assertRaises(KeyError):
            _ = REGULARITY_SCALE.get_support_level(
                quantifier, 1.0, 100, 0
            )

    def test_incorrect_key_1(self):
        quantifier = "never"
        with self.assertRaises(KeyError):
            _ = REGULARITY_SCALE.get_support_level(
                quantifier, 1.0, 100, 0
            )


if __name__ == '__main__':
    unittest.main()