import unittest

from data_utils.gecodb_compound_parser import Compound, Stem, Linker


class TestGeCoDBParser(unittest.TestCase):

    def test_zero_0(self):
        # parse compound
        gecodb = "frage_stellung"
        compound = Compound(gecodb)
        # compare components and their properties
        expected_components = [
            Stem("frage", span=(0, 5)),
            Linker("_", span=(5, 5)),
            Stem("stellung", span=(5, 13))
        ]
        actual_components = compound.components
        self.assertListEqual(expected_components, actual_components)
        # compare linker properties
        self.assertEqual(compound.linkers[0].morph, "")
        self.assertEqual(compound.linkers[0].adds_umlaut, False)
        # compare pretty form
        expected_lemma = "fragestellung"
        actual_lemma = compound.lemma
        self.assertEqual(expected_lemma, actual_lemma)

    def test_zero_1(self):
        # parse compound
        gecodb = "ring_finger"
        compound = Compound(gecodb)
        # compare components and their properties
        expected_components = [
            Stem("ring", span=(0, 4)),
            Linker("_", span=(4, 4)),
            Stem("finger", span=(4, 10))
        ]
        actual_components = compound.components
        self.assertListEqual(expected_components, actual_components)
        # compare linker properties
        self.assertEqual(compound.linkers[0].morph, "")
        self.assertEqual(compound.linkers[0].adds_umlaut, False)
        # compare pretty form
        expected_lemma = "ringfinger"
        actual_lemma = compound.lemma
        self.assertEqual(expected_lemma, actual_lemma)

    def test_zero_2(self):
        # parse compound
        gecodb = "tier_schutz_verein"
        compound = Compound(gecodb)
        # compare components and their properties
        expected_components = [
            Stem("tier", span=(0, 4)),
            Linker("_", span=(4, 4)),
            Stem("schutz", span=(4, 10)),
            Linker("_", span=(10, 10)),
            Stem("verein", span=(10, 16))
        ]
        actual_components = compound.components
        self.assertListEqual(expected_components, actual_components)
        # compare linker properties
        self.assertEqual(compound.linkers[0].morph, "")
        self.assertEqual(compound.linkers[0].adds_umlaut, False)
        self.assertEqual(compound.linkers[1].morph, "")
        self.assertEqual(compound.linkers[1].adds_umlaut, False)
        # compare pretty form
        expected_lemma = "tierschutzverein"
        actual_lemma = compound.lemma
        self.assertEqual(expected_lemma, actual_lemma)


    def test_explicit_0(self):
        # parse compound
        gecodb = "hund_+e_leine"
        compound = Compound(gecodb)
        # compare components and their properties
        expected_components = [
            Stem("hund", span=(0, 4)),
            Linker("_+e_", allomorph="e", span=(4, 5)),
            Stem("leine", span=(5, 10))
        ]
        actual_components = compound.components
        self.assertListEqual(expected_components, actual_components)
        # compare linker properties
        self.assertEqual(compound.linkers[0].morph, "e")
        self.assertEqual(compound.linkers[0].adds_umlaut, False)
        # compare pretty form
        expected_lemma = "hundeleine"
        actual_lemma = compound.lemma
        self.assertEqual(expected_lemma, actual_lemma)

    def test_explicit_1(self):
        # parse compound
        gecodb = "nerv_+en_system"
        compound = Compound(gecodb)
        # compare components and their properties
        expected_components = [
            Stem("nerv", span=(0, 4)),
            Linker("_+en_", allomorph="en", span=(4, 6)),
            Stem("system", span=(6, 12))
        ]
        actual_components = compound.components
        self.assertListEqual(expected_components, actual_components)
        # compare linker properties
        self.assertEqual(compound.linkers[0].morph, "en")
        self.assertEqual(compound.linkers[0].adds_umlaut, False)
        # compare pretty form
        expected_lemma = "nervensystem"
        actual_lemma = compound.lemma
        self.assertEqual(expected_lemma, actual_lemma)

    def test_explicit_2(self):
        # parse compound
        gecodb = "rente_+n_versicherung"
        compound = Compound(gecodb)
        # compare components and their properties
        expected_components = [
            Stem("rente", span=(0, 5)),
            Linker("_+n_", allomorph="n", span=(5, 6)),
            Stem("versicherung", span=(6, 18))
        ]
        actual_components = compound.components
        self.assertListEqual(expected_components, actual_components)
        # compare linker properties
        self.assertEqual(compound.linkers[0].morph, "en")
        self.assertEqual(compound.linkers[0].adds_umlaut, False)
        # compare pretty form
        expected_lemma = "rentenversicherung"
        actual_lemma = compound.lemma
        self.assertEqual(expected_lemma, actual_lemma)

    def test_explicit_3(self):
        # parse compound
        gecodb = "bund_+es_verfassung_+s_gericht"
        compound = Compound(gecodb)
        # compare components and their properties
        expected_components = [
            Stem("bund", span=(0, 4)),
            Linker("_+es_", allomorph="es", span=(4, 6)),
            Stem("verfassung", span=(6, 16)),
            Linker("_+s_", allomorph="s", span=(16, 17)),
            Stem("gericht", span=(17, 24))
        ]
        actual_components = compound.components
        self.assertListEqual(expected_components, actual_components)
        # compare linker properties
        self.assertEqual(compound.linkers[0].morph, "es")
        self.assertEqual(compound.linkers[0].adds_umlaut, False)
        self.assertEqual(compound.linkers[1].morph, "s")
        self.assertEqual(compound.linkers[1].adds_umlaut, False)
        # compare pretty form
        expected_lemma = "bundesverfassungsgericht"
        actual_lemma = compound.lemma
        self.assertEqual(expected_lemma, actual_lemma)


    def test_explicit_umlaut_0(self):
        # parse compound
        gecodb = "mangel_+=_rüge"
        compound = Compound(gecodb)
        # compare components and their properties
        expected_components = [
            Stem("mangel", span=(0, 6)),
            Linker("_+=_", span=(6, 6)),
            Stem("rüge", span=(6, 10))
        ]
        expected_components[0].allomorph = "mängel"   # can't set in constructor
        actual_components = compound.components
        self.assertListEqual(expected_components, actual_components)
        # compare linker properties
        self.assertEqual(compound.linkers[0].morph, "")
        self.assertEqual(compound.linkers[0].adds_umlaut, True)
        # compare pretty form
        expected_lemma = "mängelrüge"
        actual_lemma = compound.lemma
        self.assertEqual(expected_lemma, actual_lemma)

    def test_explicit_umlaut_1(self):
        # parse compound
        gecodb = "gast_+=e_buch"
        compound = Compound(gecodb)
        # compare components and their properties
        expected_components = [
            Stem("gast", span=(0, 4)),
            Linker("_+=e_", allomorph="e", span=(4, 5)),
            Stem("buch", span=(5, 9))
        ]
        expected_components[0].allomorph = "gäst"   # can't set in constructor
        actual_components = compound.components
        self.assertListEqual(expected_components, actual_components)
        # compare linker properties
        self.assertEqual(compound.linkers[0].morph, "e")
        self.assertEqual(compound.linkers[0].adds_umlaut, True)
        # compare pretty form
        expected_lemma = "gästebuch"
        actual_lemma = compound.lemma
        self.assertEqual(expected_lemma, actual_lemma)

    def test_explicit_umlaut_2(self):
        # parse compound
        gecodb = "gut_+=er_wagen"
        compound = Compound(gecodb)
        # compare components and their properties
        expected_components = [
            Stem("gut", span=(0, 3)),
            Linker("_+=er_", allomorph="er", span=(3, 5)),
            Stem("wagen", span=(5, 10))
        ]
        expected_components[0].allomorph = "güt"   # can't set in constructor
        actual_components = compound.components
        self.assertListEqual(expected_components, actual_components)
        # compare linker properties
        self.assertEqual(compound.linkers[0].morph, "er")
        self.assertEqual(compound.linkers[0].adds_umlaut, True)
        # compare pretty form
        expected_lemma = "güterwagen"
        actual_lemma = compound.lemma
        self.assertEqual(expected_lemma, actual_lemma)


    def test_complex_compound_0(self):
        # parse compound
        gecodb = "schaden_+s_ersatz_anspruch"
        compound = Compound(gecodb)
        # compare components and their properties
        expected_components = [
            Stem("schaden", span=(0, 7)),
            Linker("_+s_", allomorph="s", span=(7, 8)),
            Stem("ersatz", span=(8, 14)),
            Linker("_", span=(14, 14)),
            Stem("anspruch", span=(14, 22))
        ]
        actual_components = compound.components
        self.assertListEqual(expected_components, actual_components)
        # compare linker properties
        self.assertEqual(compound.linkers[0].morph, "s")
        self.assertEqual(compound.linkers[0].adds_umlaut, False)
        self.assertEqual(compound.linkers[1].morph, "")
        self.assertEqual(compound.linkers[1].adds_umlaut, False)
        # compare pretty form
        expected_lemma = "schadensersatzanspruch"
        actual_lemma = compound.lemma
        self.assertEqual(expected_lemma, actual_lemma)

    def test_complex_compound_1(self):
        # parse compound
        gecodb = "bund_+es_arzt_+=e_kammer"
        compound = Compound(gecodb)
        # compare components and their properties
        expected_components = [
            Stem("bund", span=(0, 4)),
            Linker("_+es_", allomorph="es", span=(4, 6)),
            Stem("arzt", span=(6, 10)),
            Linker("_+=e_", allomorph="e", span=(10, 11)),
            Stem("kammer", span=(11, 17))
        ]
        expected_components[2].allomorph = "ärzt"   # can't set in constructor
        actual_components = compound.components
        self.assertListEqual(expected_components, actual_components)
        # compare linker properties
        self.assertEqual(compound.linkers[0].morph, "es")
        self.assertEqual(compound.linkers[0].adds_umlaut, False)
        self.assertEqual(compound.linkers[1].morph, "e")
        self.assertEqual(compound.linkers[1].adds_umlaut, True)
        # compare pretty form
        expected_lemma = "bundesärztekammer"
        actual_lemma = compound.lemma
        self.assertEqual(expected_lemma, actual_lemma)


if __name__ == '__main__':
    unittest.main()