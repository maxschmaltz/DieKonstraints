import unittest

from data_utils.gecodb_compound_parser import Compound
from check_applicability.applicability_checkers import *
from check_applicability.applicability_checkers import (
    _has_linker,
    _has_no_linker,
    _is_of_plural,
    _is_of_zero_plural,
    _has_no_plural,
    _is_of_genitive,
    _is_of_gender,
    _is_mixed,
    _is_simplex,
    _is_derived,
    _is_deverbal,
    _is_deadjective,
    _is_prefixed,
    _ends_with_sfx,
    _phone_has_property,
    _is_vowel,
    _is_consonant,
    _get_last_cons_cluster,
    _ends_with_phon,
    _ends_with_phon_schwa,
    _has_n_syllables,
    _is_monosyllabic,
    _is_syl_stressed,
    _is_trochaic,
    _is_last_syl_stressed
)


# Tests for helper functions

class TestHasLinker(unittest.TestCase):
    
    def test_has_no_linker_00(self):
        compound = Compound("land_kreis")
        self.assertTrue(
            _has_no_linker(compound)
        )

    def test_has_no_linker_01(self):
        compound = Compound("land_kreis")
        self.assertFalse(
            _has_linker(compound, "es")
        )

    
    def test_has_no_linker_10(self):
        compound = Compound("haus_tür")
        self.assertTrue(
            _has_no_linker(compound)
        )

    def test_has_no_linker_11(self):
        compound = Compound("haus_tür")
        self.assertFalse(
            _has_linker(compound, "er")
        )


    def test_has_linker_00(self):
        compound = Compound("land_+es_regierung")
        self.assertTrue(
            _has_linker(compound, "es")
        )

    def test_has_linker_01(self):
        compound = Compound("land_+es_regierung")
        self.assertFalse(
            _has_no_linker(compound)
        )


    def test_has_linker_10(self):
        compound = Compound("blume_+n_topf")
        self.assertTrue(
            _has_linker(compound, "en")
        )

    def test_has_linker_11(self):
        compound = Compound("blume_+n_topf")
        self.assertFalse(
            _has_linker(compound, "s")
        )


    def test_has_linker_20(self):
        compound = Compound("stadt_+=e_tag")
        self.assertTrue(
            _has_linker(compound, "e", adds_umlaut=True)
        )

    def test_has_linker_21(self):
        compound = Compound("stadt_+=e_tag")
        self.assertFalse(
            _has_linker(compound, "e", adds_umlaut=False)
        )


    def test_has_linker_30(self):
        compound = Compound("mutter_+=_zentrum")
        self.assertTrue(
            _has_linker(compound, adds_umlaut=True)
        )

    def test_has_linker_31(self):
        compound = Compound("mutter_+=_zentrum")
        self.assertFalse(
            _has_linker(compound, adds_umlaut=False)
        )



class TestIsOfPlural(unittest.TestCase):

    def test_is_of_zero_plural_00(self):
        self.assertTrue(
            _is_of_zero_plural("teufel")
        )

    def test_is_of_zero_plural_01(self):
        self.assertFalse(
            _is_of_plural("teufel", "s")
        )


    def test_is_of_zero_plural_10(self):
        self.assertTrue(
            _is_of_zero_plural("essen")
        )

    def test_is_of_zero_plural_11(self):
        self.assertFalse(
            _is_of_plural("essen", "n")
        )


    def test_is_of_plural_00(self):
        self.assertTrue(
            _is_of_plural("frage", "en")
        )

    def test_is_of_plural_01(self):
        self.assertFalse(
            _is_of_zero_plural("frage")
        )


    def test_is_of_plural_10(self):
        self.assertTrue(
            _is_of_plural("burg", "en")
        )

    def test_is_of_plural_11(self):
        self.assertFalse(
            _is_of_plural("burg", "e")
        )


    def test_is_of_plural_20(self):
        self.assertTrue(
            _is_of_plural("hand", "e", adds_umlaut=True)
        )

    def test_is_of_plural_21(self):
        self.assertFalse(
            _is_of_plural("hand", "e", adds_umlaut=False)
        )


    def test_is_of_plural_30(self):
        self.assertTrue(
            _is_of_plural("kind", "er", adds_umlaut=True)
        )

    def test_is_of_plural_31(self):
        self.assertFalse(
            _is_of_plural("kind", "er", adds_umlaut=False)
        )


    def test_is_of_plural_40(self):
        self.assertTrue(
            _is_of_plural("vogel", "", adds_umlaut=True)
        )

    def test_is_of_plural_41(self):
        self.assertFalse(
            _is_of_zero_plural("vogel")
        )


    def test_is_of_plural_50(self):
        self.assertTrue(
            _is_of_plural("auto", "s")
        )

    def test_is_of_plural_51(self):
        self.assertFalse(
            _is_of_zero_plural("auto")
        )


    def test_is_of_plural_6(self):
        self.assertTrue(
            _is_of_plural("oper", "en")
        )

    def test_is_of_plural_7(self):
        self.assertTrue(
            _is_of_plural("zwiebel", "en")
        )


    def test_is_of_plural_8(self):
        self.assertTrue(
            _is_of_plural("ergebnis", "e", dupl=True)
        )

    def test_is_of_plural_9(self):
        self.assertTrue(
            _is_of_plural("freundin", "en", dupl=True)
        )


    def test_is_multiple_plural_00(self):
        self.assertTrue(
            _is_of_plural("vormund", "e")
        )

    def test_is_multiple_plural_01(self):
        self.assertTrue(
            _is_of_plural("vormund", "er", adds_umlaut=True)
        )


    def test_is_multiple_plural_10(self):
        self.assertTrue(
            _is_of_plural("licht", "e")
        )

    def test_is_multiple_plural_11(self):
        self.assertTrue(
            _is_of_plural("licht", "er", adds_umlaut=True)
        )


    def test_is_multiple_plural_20(self):
        self.assertTrue(
            _is_of_plural("kran", "e")
        )

    def test_is_multiple_plural_21(self):
        self.assertTrue(
            _is_of_plural("kran", "e", adds_umlaut=True)
        )


    def test_has_no_plural_00(self):
        self.assertTrue(
            _has_no_plural("personal")
        )

    def test_has_no_plural_01(self):
        self.assertFalse(
            _is_of_plural("personal", "e")
        )


    def test_has_no_plural_10(self):
        self.assertTrue(
            _has_no_plural("unverständnis")
        )

    def test_has_no_plural_11(self):
        self.assertFalse(
            _is_of_plural("unverständnis", "en")
        )


    def test_has_no_plural_20(self):
        self.assertFalse(
            _has_no_plural("kanal")
        )


    def test_has_no_plural_20(self):
        self.assertFalse(
            _has_no_plural("ergebnis")
        )


class TestIsOfGenitive(unittest.TestCase):

    def test_is_of_genitive_00(self):
        self.assertTrue(
            _is_of_genitive("mann", "s")
        )

    def test_is_of_genitive_01(self):
        self.assertFalse(
            _is_of_genitive("mann", "")
        )


    def test_is_of_genitive_10(self):
        self.assertTrue(
            _is_of_genitive("vogel", "s")
        )

    def test_is_of_genitive_11(self):
        self.assertFalse(
            _is_of_genitive("vogel", "")
        )


    def test_is_of_genitive_20(self):
        self.assertTrue(
            _is_of_genitive("liebe", "")
        )

    def test_is_of_genitive_21(self):
        self.assertFalse(
            _is_of_genitive("liebe", "s")
        )


    def test_is_of_genitive_30(self):
        self.assertTrue(
            _is_of_genitive("hand", "")
        )

    def test_is_of_genitive_31(self):
        self.assertFalse(
            _is_of_genitive("hand", "s")
        )


class TestIsOfGender(unittest.TestCase):

    def test_is_of_gender_m_00(self):
        self.assertTrue(
            _is_of_gender("mann", "m")
        )

    def test_is_of_gender_m_01(self):
        self.assertFalse(
            _is_of_gender("mann", "f")
        )


    def test_is_of_gender_m_10(self):
        self.assertTrue(
            _is_of_gender("baum", "m")
        )

    def test_is_of_gender_m_11(self):
        self.assertFalse(
            _is_of_gender("baum", "n")
        )


    def test_is_of_gender_f_00(self):
        self.assertTrue(
            _is_of_gender("frau", "f")
        )

    def test_is_of_gender_f_01(self):
        self.assertFalse(
            _is_of_gender("frau", "m")
        )


    def test_is_of_gender_f_10(self):
        self.assertTrue(
            _is_of_gender("erlaubnis", "f")
        )

    def test_is_of_gender_f_11(self):
        self.assertFalse(
            _is_of_gender("erlaubnis", "n")
        )


    def test_is_of_gender_n_00(self):
        self.assertTrue(
            _is_of_gender("kind", "n")
        )

    def test_is_of_gender_n_01(self):
        self.assertFalse(
            _is_of_gender("kind", "f")
        )


    def test_is_of_gender_n_10(self):
        self.assertTrue(
            _is_of_gender("buch", "n")
        )

    def test_is_of_gender_n_11(self):
        self.assertFalse(
            _is_of_gender("buch", "f")
        )


    def test_is_of_multiple_gender_00(self):
        self.assertTrue(
            _is_of_gender("teil", "m")
        )

    def test_is_of_multiple_gender_01(self):
        self.assertTrue(
            _is_of_gender("teil", "n")
        )

    def test_is_of_multiple_gender_02(self):
        self.assertFalse(
            _is_of_gender("teil", "f")
        )


    def test_is_of_multiple_gender_10(self):
        self.assertTrue(
            _is_of_gender("gummi", "m")
        )

    def test_is_of_multiple_gender_11(self):
        self.assertTrue(
            _is_of_gender("gummi", "n")
        )

    def test_is_of_multiple_gender_12(self):
        self.assertFalse(
            _is_of_gender("gummi", "f")
        )


class TestIsMixed(unittest.TestCase):

    def test_is_mixed_0(self):
        self.assertTrue(
            _is_mixed("bett")
        )

    def test_is_mixed_1(self):
        self.assertTrue(
            _is_mixed("staat")
        )

    def test_is_mixed_2(self):
        self.assertTrue(
            _is_mixed("ohr")
        )

    def test_is_mixed_3(self):
        self.assertTrue(
            _is_mixed("auge")
        )


    def test_is_not_mixed_0(self):
        self.assertFalse(
            _is_mixed("kerze")
        )

    def test_is_not_mixed_1(self):
        self.assertFalse(
            _is_mixed("teil")
        )

    def test_is_not_mixed_2(self):
        self.assertFalse(
            _is_mixed("tisch")
        )

    def test_is_not_mixed_3(self):
        self.assertFalse(
            _is_mixed("auto")
        )



class TestIsDerived(unittest.TestCase):

    def test_is_simplex_0(self):
        self.assertTrue(
            _is_simplex("ehre")
        )

    def test_is_simplex_1(self):
        self.assertFalse(
            _is_simplex("ehrlichkeit")
        )

    def test_is_simplex_2(self):
        self.assertFalse(
            _is_simplex("braten")
        )


    def test_is_derived_0(self):
        self.assertTrue(
            _is_derived("abbau")
        )

    def test_is_derived_1(self):
        self.assertFalse(
            _is_derived("abend")
        )


class TestIsDeverbalDeadjective(unittest.TestCase):

    def test_is_deverbal_0(self):
        self.assertTrue(
            _is_deverbal("abfahrt")
        )

    def test_is_deverbal_1(self):
        self.assertTrue(
            _is_deverbal("eintritt")
        )

    def test_is_deverbal_2(self):
        self.assertTrue(
            _is_deverbal("stich")
        )

    def test_is_deverbal_3(self):
        self.assertTrue(
            _is_deverbal("leben")
        )


    def test_is_deverbal_4(self):
        self.assertFalse(
            _is_deverbal("liebe")
        )

    def test_is_deverbal_5(self):
        self.assertFalse(
            _is_deverbal("klarheit")
        )

    def test_is_deverbal_6(self):
        self.assertFalse(
            _is_deverbal("tür")
        )


    def test_is_deadjective_0(self):
        self.assertTrue(
            _is_deadjective("klarheit")
        )

    def test_is_deadjective_1(self):
        self.assertTrue(
            _is_deadjective("alter")
        )

    def test_is_deadjective_2(self):
        self.assertTrue(
            _is_deadjective("besserung")
        )

    # def test_is_deadjective_3(self):
    #     self.assertTrue(
    #         _is_deadjective("junge")  # "junge" filtered out
    #     )

    
    def test_is_deadjective_4(self):
        self.assertFalse(
            _is_deadjective("übung")
        )

    def test_is_deadjective_5(self):
        self.assertFalse(
            _is_deadjective("leben")
        )

    def test_is_deadjective_6(self):
        self.assertFalse(
            _is_deadjective("tür")
        )


class TestIsPrefixed(unittest.TestCase):

    def test_is_prefixed_0(self):
        self.assertTrue(
            _is_prefixed("abfahrt")
        )

    def test_is_prefixed_1(self):
        self.assertTrue(
            _is_prefixed("einblick")
        )

    def test_is_prefixed_2(self):
        self.assertTrue(
            _is_prefixed("durchschnitt")
        )

    def test_is_prefixed_3(self):
        self.assertTrue(
            _is_prefixed("mitglied")
        )

    def test_is_prefixed_4(self):
        self.assertTrue(
            _is_prefixed("fortschritt")
        )

    def test_is_prefixed_5(self):
        self.assertTrue(
            _is_prefixed("hintergrund")
        )


    def test_is_not_prefixed_0(self):
        self.assertFalse(
            _is_prefixed("abend")
        )

    def test_is_not_prefixed_1(self):
        self.assertFalse(
            _is_prefixed("beere")
        )

    def test_is_not_prefixed_2(self):
        self.assertFalse(
            _is_prefixed("version")
        )


class TestEndsWithSfx(unittest.TestCase):

    def test_ends_with_sfx_00(self):
        self.assertTrue(
            _ends_with_sfx("übung", "ung")
        )

    def test_ends_with_sfx_01(self):
        self.assertFalse(
            _ends_with_sfx("übung", "heit")
        )


    def test_ends_with_sfx_10(self):
        self.assertTrue(
            _ends_with_sfx("schicksal", "sal")
        )

    def test_ends_with_sfx_11(self):
        self.assertFalse(
            _ends_with_sfx("schicksal", "ion")
        )

    
    def test_ends_with_sfx_20(self):
        self.assertTrue(
            _ends_with_sfx("eigentum", ["tum", "nis", "chen"])
        )

    def test_ends_with_sfx_21(self):
        self.assertFalse(
            _ends_with_sfx("eigentum", ["heit", "ler", "igkeit"])
        )


    def test_ends_with_sfx_30(self):
        self.assertTrue(
            _ends_with_sfx("feigling", ["ität", "ling"])
        )

    def test_ends_with_sfx_31(self):
        self.assertFalse(
            _ends_with_sfx("feigling", ["el", "nis", "at"])
        )


    def test_ends_with_sfx_4(self):
        self.assertFalse(
            _ends_with_sfx("mutter", "er")
        )

    def test_ends_with_sfx_5(self):
        self.assertFalse(
            _ends_with_sfx("teufel", ["el", "sel"])
        )



class TestPhoneProperties(unittest.TestCase):

    def test_is_vowel_0(self):
        self.assertTrue(
            _is_vowel("a")
        )

    def test_is_vowel_1(self):
        self.assertTrue(
            _is_vowel("ə")
        )

    def test_is_vowel_2(self):
        self.assertTrue(
            _is_vowel("ɶ")
        )

    def test_is_vowel_3(self):
        self.assertFalse(
            _is_vowel("w")
        )


    def test_is_consonant_0(self):
        self.assertTrue(
            _is_consonant("t")
        )

    def test_is_consonant_1(self):
        self.assertTrue(
            _is_consonant("ʃ")
        )

    def test_is_consonant_2(self):
        self.assertTrue(
            _is_consonant("ʝ")
        )

    def test_is_consonant_3(self):
        self.assertTrue(
            _is_consonant("w")
        )

    def test_is_consonant_4(self):
        self.assertFalse(
            _is_consonant("ɶ")
        )


    def test_phone_has_property_0(self):
        self.assertTrue(
            _phone_has_property("ʝ", "voiced")
        )

    def test_phone_has_property_1(self):
        self.assertTrue(
            _phone_has_property("ʝ", "non-sibilant-fricative")
        )

    def test_phone_has_property_2(self):
        self.assertTrue(
            _phone_has_property("ʝ", "palatal")
        )

    def test_phone_has_property_3(self):
        self.assertFalse(
            _phone_has_property("ʝ", "rounded")
        )


    def test_phone_has_property_4(self):
        self.assertTrue(
            _phone_has_property("b", "voiced")
        )

    def test_phone_has_property_5(self):
        self.assertTrue(
            _phone_has_property("b", "plosive")
        )

    def test_phone_has_property_6(self):
        self.assertTrue(
            _phone_has_property("b", "bilabial")
        )

    def test_phone_has_property_7(self):
        self.assertFalse(
            _phone_has_property("b", "alveolar")
        )


    def test_phone_has_property_8(self):
        self.assertTrue(
            _phone_has_property(
                "ʃ",
                ["voiceless", "sibilant-fricative", "palato-alveolar"]
            )
        )

    def test_phone_has_property_9(self):
        self.assertFalse(
            _phone_has_property(
                "ʃ",
                ["voiced", "sibilant-fricative", "palato-alveolar"]
            )
        )

    def test_phone_has_property_10(self):
        self.assertFalse(
            _phone_has_property(
                "ʃ",
                ["voiceless", "non-sibilant-fricative", "palato-alveolar"]
            )
        )

    def test_phone_has_property_11(self):
        self.assertFalse(
            _phone_has_property(
                "ʃ",
                ["voiceless", "sibilant-fricative", "alveolar"]
            )
        )


    def test_phone_has_property_12(self):
        self.assertTrue(
            _phone_has_property("ɨ", "central")
        )

    def test_phone_has_property_13(self):
        self.assertTrue(
            _phone_has_property("ɨ", "close")
        )

    def test_phone_has_property_14(self):
        self.assertTrue(
            _phone_has_property("ɨ", "unrounded")
        )

    def test_phone_has_property_15(self):
        self.assertFalse(
            _phone_has_property("ɨ", "tense")
        )


    def test_phone_has_property_16(self):
        self.assertTrue(
            _phone_has_property(
                "ʉ",
                ["central", "close", "rounded"]
            )
        )

    def test_phone_has_property_17(self):
        self.assertFalse(
            _phone_has_property(
                "ʉ",
                ["front", "close", "rounded"]
            )
        )

    def test_phone_has_property_18(self):
        self.assertFalse(
            _phone_has_property(
                "ʉ",
                ["central", "open-mid", "rounded"]
            )
        )

    def test_phone_has_property_19(self):
        self.assertFalse(
            _phone_has_property(
                "ʉ",
                ["central", "close", "unrounded"]
            )
        )
    

class TestGetLastConsCluster(unittest.TestCase):

    def test_get_last_cons_cluster_0(self):
        self.assertEqual(
            _get_last_cons_cluster("kind"),
            "nt"
        )

    def test_get_last_cons_cluster_1(self):
        self.assertEqual(
            _get_last_cons_cluster("orden"),
            "n"
        )

    def test_get_last_cons_cluster_2(self):
        self.assertEqual(
            _get_last_cons_cluster("herbst"),
            "ʁpst"
        )

    def test_get_last_cons_cluster_3(self):
        self.assertEqual(
            _get_last_cons_cluster("karte"),
            ""
        )


class TestEndsWithPhon(unittest.TestCase):

    def test_ends_with_phon_00(self):
        self.assertTrue(
            _ends_with_phon("kind", ["t"])
        )

    def test_ends_with_phon_01(self):
        self.assertFalse(
            _ends_with_phon("kind", ["d"])
        )


    def test_ends_with_phon_10(self):
        self.assertTrue(
            _ends_with_phon("orden", "ən")
        )

    def test_ends_with_phon_11(self):
        self.assertFalse(
            _ends_with_phon("orden", "en")
        )


    def test_ends_with_phon_schwa_0(self):
        self.assertTrue(
            _ends_with_phon_schwa("blume")
        )

    def test_ends_with_phon_schwa_1(self):
        self.assertTrue(
            _ends_with_phon_schwa("karte")
        )

    def test_ends_with_phon_schwa_2(self):
        self.assertFalse(
            _ends_with_phon_schwa("auto")
        )


class HasNSyllables(unittest.TestCase):

    def test_has_n_syllables_00(self):
        self.assertTrue(
            _has_n_syllables("mann", 1)
        )

    def test_has_n_syllables_01(self):
        self.assertTrue(
            _is_monosyllabic("mann")
        )

    def test_has_n_syllables_02(self):
        self.assertFalse(
            _has_n_syllables("mann", 2)
        )


    def test_has_n_syllables_10(self):
        self.assertTrue(
            _has_n_syllables("knie", 1)
        )

    def test_has_n_syllables_11(self):
        self.assertTrue(
            _is_monosyllabic("knie")
        )

    def test_has_n_syllables_12(self):
        self.assertFalse(
            _has_n_syllables("knie", 2)
        )


    def test_has_n_syllables_20(self):
        self.assertTrue(
            _has_n_syllables("auge", 2)
        )

    def test_has_n_syllables_21(self):
        self.assertFalse(
            _is_monosyllabic("auge")
        )

    def test_has_n_syllables_22(self):
        self.assertFalse(
            _has_n_syllables("auge", 3)
        )


    def test_has_n_syllables_30(self):
        self.assertTrue(
            _has_n_syllables("koketterie", 4)
        )

    def test_has_n_syllables_31(self):
        self.assertFalse(
            _has_n_syllables("koketterie", 5)
        )


class TestIsSylStressed(unittest.TestCase):

    def test_is_syl_stressed_00(self):
        self.assertTrue(
            _is_syl_stressed("mann", 0)
        )

    def test_is_syl_stressed_01(self):
        self.assertTrue(
            _is_syl_stressed("mann", -1)
        )

    def test_is_syl_stressed_02(self):
        self.assertFalse(
            _is_syl_stressed("mann", 3)
        )


    def test_is_syl_stressed_10(self):
        self.assertTrue(
            _is_syl_stressed("auge", 0)
        )

    def test_is_syl_stressed_11(self):
        self.assertTrue(
            _is_syl_stressed("auge", -2)
        )

    def test_is_syl_stressed_12(self):
        self.assertFalse(
            _is_syl_stressed("auge", 1)
        )


    def test_is_syl_stressed_20(self):
        self.assertTrue(
            _is_syl_stressed("koketterie", 3)
        )

    def test_is_syl_stressed_21(self):
        self.assertTrue(
            _is_syl_stressed("koketterie", -1)
        )

    def test_is_syl_stressed_22(self):
        self.assertFalse(
            _is_syl_stressed("koketterie", 2)
        )

    
    def test_is_trochaic_0(self):
        self.assertTrue(
            _is_trochaic("blume")
        )

    def test_is_trochaic_1(self):
        self.assertTrue(
            _is_trochaic("krieger")
        )

    def test_is_trochaic_2(self):
        self.assertTrue(
            _is_trochaic("uhu")
        )

    def test_is_trochaic_3(self):
        self.assertFalse(
            _is_trochaic("baum")
        )

    def test_is_trochaic_4(self):
        self.assertFalse(
            _is_trochaic("bedarf")
        )

    def test_is_trochaic_5(self):
        self.assertFalse(
            _is_trochaic("komiker")
        )


    def test_is_last_syl_stressed_0(self):
        self.assertTrue(
            _is_last_syl_stressed("baum")
        )

    def test_is_last_syl_stressed_1(self):
        self.assertTrue(
            _is_last_syl_stressed("tür")
        )

    def test_is_last_syl_stressed_2(self):
        self.assertTrue(
            _is_last_syl_stressed("chemie")
        )

    def test_is_last_syl_stressed_3(self):
        self.assertTrue(
            _is_last_syl_stressed("bedarf")
        )

    def test_is_last_syl_stressed_4(self):
        self.assertFalse(
            _is_last_syl_stressed("blume")
        )

    def test_is_last_syl_stressed_5(self):
        self.assertFalse(
            _is_last_syl_stressed("karte")
        )



# Tests for applicability checkers

class TestApplicabilityCheckersDef0(unittest.TestCase):
    
    # def-0
    #
    # The majority of compounds have a zero linker.
    # Zero linker is default for German compounds.
        
    def test_def_0_is_applicable_0(self):
        compound = Compound("land_kreis")
        self.assertTrue(
            def_0_is_applicable(compound)
        )

    def test_def_0_applies_0(self):
        compound = Compound("land_kreis")
        self.assertTrue(
            def_0_applies(compound)
        )

    
    def test_def_0_is_applicable_1(self):
        compound = Compound("haus_tür")
        self.assertTrue(
            def_0_is_applicable(compound)
        )

    def test_def_0_applies_1(self):
        compound = Compound("haus_tür")
        self.assertTrue(
            def_0_applies(compound)
        )


    def test_vdef_0_is_applicable_3(self):
        compound = Compound("land_+es_regierung")
        self.assertTrue(
            def_0_is_applicable(compound)
        )

    def test_def_0_applies_3(self):
        compound = Compound("land_+es_regierung")
        self.assertFalse(
            def_0_applies(compound)
        )


    def test_def_0_is_applicable_4(self):
        compound = Compound("haus_+=er_block")
        self.assertTrue(
            def_0_is_applicable(compound)
        )

    def test_def_0_applies_4(self):
        compound = Compound("haus_+=er_block")
        self.assertFalse(
            def_0_applies(compound)
        )


    def test_def_0_is_applicable_5(self):
        compound = Compound("stadt_+=e_tag")
        self.assertTrue(
            def_0_is_applicable(compound)
        )

    def test_def_0_applies_5(self):
        compound = Compound("stadt_+=e_tag")
        self.assertFalse(
            def_0_applies(compound)
        )



class TestApplicabilityCheckersPlur0(unittest.TestCase):
    
    # p2l:decl_cl:pl:#0-0|def-0
    #
    # First constituents that are constituted
    # by simplex masculine or neuter nouns
    # that build the plural form with a zero ending
    # and simplex or complex feminine nouns
    # that build the plural form with a zero ending
    # attach a zero linker almost regularly.
        
    def test_plur_0_is_applicable_0(self):
        compound = Compound("schlitten_fahrt")
        self.assertTrue(
            plur_0_is_applicable(compound)
        )

    def test_plur_0_applies_0(self):
        compound = Compound("schlitten_fahrt")
        self.assertTrue(
            plur_0_applies(compound)
        )


    def test_plur_0_is_applicable_1(self):
        compound = Compound("wagen_rad")
        self.assertTrue(
            plur_0_is_applicable(compound)
        )

    def test_plur_0_applies_1(self):
        compound = Compound("wagen_rad")
        self.assertTrue(
            plur_0_applies(compound)
        )

    
    def test_plur_0_is_applicable_2(self):
        compound = Compound("ufer_promenade")
        self.assertTrue(
            plur_0_is_applicable(compound)
        )

    def test_plur_0_applies_2(self):
        compound = Compound("ufer_promenade")
        self.assertTrue(
            plur_0_applies(compound)
        )

    
    def test_plur_0_is_applicable_3(self):
        compound = Compound("orden_+s_bruder")
        self.assertTrue(
            plur_0_is_applicable(compound)
        )

    def test_plur_0_applies_3(self):
        compound = Compound("orden_+s_bruder")
        self.assertFalse(
            plur_0_applies(compound)
        )


    def test_plur_0_is_applicable_4(self):
        compound = Compound("teufel_+s_werk")
        self.assertTrue(
            plur_0_is_applicable(compound)
        )

    def test_plur_0_applies_4(self):
        compound = Compound("teufel_+s_werk")
        self.assertFalse(
            plur_0_applies(compound)
        )


    def test_plur_0_is_applicable_5(self):
        compound = Compound("haus_tür")
        self.assertFalse(
            plur_0_is_applicable(compound)
        )

    def test_plur_0_is_applicable_6(self):
        compound = Compound("stadt_+=e_tag")
        self.assertFalse(
            plur_0_is_applicable(compound)
        )

    def test_plur_0_applies_7(self):
        # derivate
        compound = Compound("abkommen_+s_recht")
        self.assertFalse(
            plur_0_is_applicable(compound)
        )

    def test_plur_0_is_applicable_8(self):
        compound = Compound("brötchen_geber")
        self.assertFalse(
            plur_0_is_applicable(compound)
        )



class TestApplicabilityCheckersPlurS(unittest.TestCase):
    
    # p2l:decl_cl:pl:#s-0
    #
    # First constituents that are constituted by nouns that build
    # the plural form with -s attach a zero linker regularly.
        
    def test_plur_s_is_applicable_0(self):
        compound = Compound("balkon_möbel")
        self.assertTrue(
            plur_s_is_applicable(compound)
        )

    def test_plur_s_applies_0(self):
        compound = Compound("balkon_möbel")
        self.assertTrue(
            plur_s_applies(compound)
        )

    def test_plur_s_is_applicable_1(self):
        compound = Compound("hotel_kette")
        self.assertTrue(
            plur_s_is_applicable(compound)
        )

    def test_plur_s_applies_1(self):
        compound = Compound("hotel_kette")
        self.assertTrue(
            plur_s_applies(compound)
        )

    def test_plur_s_is_applicable_2(self):
        compound = Compound("bob_bahn")
        self.assertTrue(
            plur_s_is_applicable(compound)
        )

    def test_plur_s_applies_2(self):
        compound = Compound("bob_bahn")
        self.assertTrue(
            plur_s_applies(compound)
        )


    def test_plur_s_is_applicable_3(self):
        compound = Compound("uhu_+s_nest")
        self.assertTrue(
            plur_s_is_applicable(compound)
        )

    def test_plur_s_applies_3(self):
        compound = Compound("uhu_+s_nest")
        self.assertFalse(
            plur_s_applies(compound)
        )


    def test_plur_s_applies_4(self):
        compound = Compound("haus_tür")
        self.assertFalse(
            plur_s_is_applicable(compound)
        )


    def test_plur_s_is_applicable_5(self):
        compound = Compound("haus_+=er_block")
        self.assertFalse(
            plur_s_is_applicable(compound)
        )


    def test_plur_s_is_applicable_6(self):
        compound = Compound("stadt_+=e_tag")
        self.assertFalse(
            plur_s_is_applicable(compound)
        )



class TestApplicabilityCheckersPlurE(unittest.TestCase):
    
    # p2l:decl_cl:pl:#e-0|def-0
    #
    # First constituents that are constituted by nouns that build
    # the plural form with -e mostly have a zero linker.
        
    def test_plur_e_is_applicable_0(self):
        compound = Compound("tisch_decke")
        self.assertTrue(
            plur_e_is_applicable(compound)
        )

    def test_plur_e_applies_0(self):
        compound = Compound("tisch_decke")
        self.assertTrue(
            plur_e_applies(compound)
        )


    def test_plur_e_is_applicable_1(self):
        compound = Compound("spiel_system")
        self.assertTrue(
            plur_e_is_applicable(compound)
        )

    def test_plur_e_applies_1(self):
        compound = Compound("spiel_system")
        self.assertTrue(
            plur_e_applies(compound)
        )

    
    def test_plur_e_is_applicable_2(self):
        compound = Compound("pilz_sammler")
        self.assertTrue(
            plur_e_is_applicable(compound)
        )

    def test_plur_e_applies_2(self):
        compound = Compound("pilz_sammler")
        self.assertTrue(
            plur_e_applies(compound)
        )

    
    def test_plur_e_is_applicable_3(self):
        compound = Compound("tag_+e_gericht")
        self.assertTrue(
            plur_e_is_applicable(compound)
        )

    def test_plur_e_applies_3(self):
        compound = Compound("tag_+e_gericht")
        self.assertFalse(
            plur_e_applies(compound)
        )


    def test_plur_e_is_applicable_4(self):
        compound = Compound("spiel_+e_konsole")
        self.assertTrue(
            plur_e_is_applicable(compound)
        )

    def test_plur_e_applies_4(self):
        compound = Compound("spiel_+e_konsole")
        self.assertFalse(
            plur_e_applies(compound)
        )


    def test_plur_e_is_applicable_5(self):
        # derivate
        compound = Compound("hund_+e_leine")
        self.assertTrue(
            plur_e_is_applicable(compound)
        )

    def test_plur_e_applies_5(self):
        # derivate
        compound = Compound("hund_+e_leine")
        self.assertFalse(
            plur_e_applies(compound)
        )


    def test_plur_e_is_applicable_6(self):
        compound = Compound("haus_tür")
        self.assertFalse(
            plur_e_is_applicable(compound)
        )

    def test_plur_e_is_applicable_7(self):
        compound = Compound("stadt_+=e_tag")
        self.assertFalse(
            plur_e_is_applicable(compound)
        )


class TestApplicabilityCheckersPlurEPl:

	# p2l:decl_cl:pl:#e-0|pl_interpr-e
	#
    # First constituents that are constituted by nouns that build
    # the plural form with -e attach -e- irregularly in compounds
    # in which the second constituent forces
    # a plural meaning of the given first constituent.

    # def test_plur_e_pl_is_applicable_0(self):
    #     compound = Compound("projekt_+e_macherei")
    #     self.assertTrue(
    #         plur_e_pl_is_applicable(compound)
    #     )

    # def test_plur_e_pl_applies_0(self):
    #     compound = Compound("projekt_+e_macherei")
    #     self.assertTrue(
    #         plur_e_pl_applies(compound)
    #     )

        
    # def test_plur_e_pl_is_applicable_1(self):
    #     compound = Compound("tag_+e_buch")
    #     self.assertTrue(
    #         plur_e_pl_is_applicable(compound)
    #     )

    # def test_plur_e_pl_applies_1(self):
    #     compound = Compound("tag_+e_buch")
    #     self.assertTrue(
    #         plur_e_pl_applies(compound)
    #     )

        
    # def test_plur_e_pl_is_applicable_2(self):
    #     compound = Compound("punkt_+e_stand")
    #     self.assertTrue(
    #         plur_e_pl_is_applicable(compound)
    #     )

    # def test_plur_e_pl_applies_2(self):
    #     compound = Compound("punkt_+e_stand")
    #     self.assertTrue(
    #         plur_e_pl_applies(compound)
    #     )

        
    # def test_plur_e_pl_is_applicable_3(self):
    #     compound = Compound("pilz_sammler")
    #     self.assertTrue(
    #         plur_e_pl_is_applicable(compound)
    #     )

    # def test_plur_e_pl_applies_3(self):
    #     compound = Compound("pilz_sammler")
    #     self.assertFalse(
    #         plur_e_pl_applies(compound)
    #     )

        
    # def test_plur_e_pl_is_applicable_4(self):
    #     compound = Compound("brot_korb")
    #     self.assertTrue(
    #         plur_e_pl_is_applicable(compound)
    #     )

    # def test_plur_e_pl_applies_4(self):
    #     compound = Compound("brot_korb")
    #     self.assertFalse(
    #         plur_e_pl_applies(compound)
    #     )

        
    # def test_plur_e_pl_is_applicable_5(self):
    #     compound = Compound("jahr_zehnt")
    #     self.assertTrue(
    #         plur_e_pl_is_applicable(compound)
    #     )

    # def test_plur_e_pl_applies_5(self):
    #     compound = Compound("jahr_zehnt")
    #     self.assertFalse(
    #         plur_e_pl_applies(compound)
    #     )

        
    # def test_plur_e_pl_is_applicable_6(self):
    #     compound = Compound("tag_+e_lohn")
    #     self.assertTrue(
    #         plur_e_pl_is_applicable(compound)
    #     )

    # def test_plur_e_pl_applies_6(self):
    #     compound = Compound("tag_+e_lohn")
    #     self.assertFalse(
    #         plur_e_pl_applies(compound)
    #     )

        
    # def test_plur_e_pl_is_applicable_7(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         plur_e_pl_is_applicable(compound)
    #     )

    # def test_plur_e_pl_is_applicable_8(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         plur_e_pl_is_applicable(compound)
    #     )

	pass


class TestApplicabilityCheckersPlurEAnim:

	# p2l:decl_cl:pl:#e-0|msyl_anim-e
	#
    # First constituents that are constituted by
    # monosyllabic animal designations that build
    # the plural form with -e attach -e- irregularly.

    # def test_plur_e_anim_is_applicable_0(self):
    #     compound = Compound("hund_+e_leine")
    #     self.assertTrue(
    #         plur_e_anim_is_applicable(compound)
    #     )

    # def test_plur_e_anim_applies_0(self):
    #     compound = Compound("hund_+e_leine")
    #     self.assertTrue(
    #         plur_e_anim_applies(compound)
    #     )

        
    # def test_plur_e_anim_is_applicable_1(self):
    #     compound = Compound("swein_+e_stall")
    #     self.assertTrue(
    #         plur_e_anim_is_applicable(compound)
    #     )

    # def test_plur_e_anim_applies_1(self):
    #     compound = Compound("swein_+e_stall")
    #     self.assertTrue(
    #         plur_e_anim_applies(compound)
    #     )

        
    # def test_plur_e_anim_is_applicable_2(self):
    #     compound = Compound("pferd_+e_wagen")
    #     self.assertTrue(
    #         plur_e_anim_is_applicable(compound)
    #     )

    # def test_plur_e_anim_applies_2(self):
    #     compound = Compound("pferd_+e_wagen")
    #     self.assertTrue(
    #         plur_e_anim_applies(compound)
    #     )

        
    # def test_plur_e_anim_is_applicable_3(self):
    #     compound = Compound("hund_+s_stern")
    #     self.assertTrue(
    #         plur_e_anim_is_applicable(compound)
    #     )

    # def test_plur_e_anim_applies_3(self):
    #     compound = Compound("hund_+s_stern")
    #     self.assertFalse(
    #         plur_e_anim_applies(compound)
    #     )

        
    # def test_plur_e_anim_is_applicable_4(self):
    #     compound = Compound("schwein_kram")
    #     self.assertTrue(
    #         plur_e_anim_is_applicable(compound)
    #     )

    # def test_plur_e_anim_applies_4(self):
    #     compound = Compound("schwein_kram")
    #     self.assertFalse(
    #         plur_e_anim_applies(compound)
    #     )

        
    # def test_plur_e_anim_is_applicable_5(self):
    #     compound = Compound("schaff_stall")
    #     self.assertTrue(
    #         plur_e_anim_is_applicable(compound)
    #     )

    # def test_plur_e_anim_applies_5(self):
    #     compound = Compound("schaff_stall")
    #     self.assertFalse(
    #         plur_e_anim_applies(compound)
    #     )

        
    # def test_plur_e_anim_is_applicable_6(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         plur_e_anim_is_applicable(compound)
    #     )

    # def test_plur_e_anim_is_applicable_7(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         plur_e_anim_is_applicable(compound)
    #     )

	pass



class TestApplicabilityCheckersPlurEr(unittest.TestCase):
    
    # p2l:decl_cl:pl:#er-0/er|def-0/er
    #
    # First constituents that are constituted by nouns that build
    # the plural form with -(")er
    # mostly attach a zero linker or -(")er-.
        
    def test_plur_er_is_applicable_0(self):
        compound = Compound("buch_deckel")
        self.assertTrue(
            plur_er_is_applicable(compound)
        )

    def test_plur_er_applies_0(self):
        compound = Compound("buch_deckel")
        self.assertTrue(
            plur_er_applies(compound)
        )


    def test_plur_er_is_applicable_1(self):
        compound = Compound("buch_+=er_regal")
        self.assertTrue(
            plur_er_is_applicable(compound)
        )

    def test_plur_er_applies_1(self):
        compound = Compound("buch_+=er_regal")
        self.assertTrue(
            plur_er_applies(compound)
        )

    
    def test_plur_er_is_applicable_2(self):
        compound = Compound("kind_+=er_jacke")
        self.assertTrue(
            plur_er_is_applicable(compound)
        )

    def test_plur_er_applies_2(self):
        compound = Compound("kind_+=er_jacke")
        self.assertTrue(
            plur_er_applies(compound)
        )

    
    def test_plur_er_is_applicable_3(self):
        compound = Compound("kind_+es_alter")
        self.assertTrue(
            plur_er_is_applicable(compound)
        )

    def test_plur_er_applies_3(self):
        compound = Compound("kind_+es_alter")
        self.assertFalse(
            plur_er_applies(compound)
        )


    def test_plur_er_is_applicable_4(self):
        compound = Compound("mann_+s_volk")
        self.assertTrue(
            plur_er_is_applicable(compound)
        )

    def test_plur_er_applies_4(self):
        compound = Compound("mann_+s_volk")
        self.assertFalse(
            plur_er_applies(compound)
        )


    def test_plur_er_is_applicable_5(self):
        compound = Compound("tag_+e_gericht")
        self.assertFalse(
            plur_er_is_applicable(compound)
        )

    def test_plur_er_is_applicable_6(self):
        compound = Compound("stadt_+=e_tag")
        self.assertFalse(
            plur_er_is_applicable(compound)
        )


class TestApplicabilityCheckersPlurErSg:

	# p2l:decl_cl:pl:#er-0/er|!pl_interpr-0
	#
    # First constituents that are constituted by nouns that build
    # the plural form with -(")er
    # attach a zero linker in majority of compounds
    # in which the second constituent forces
    # a singular meaning of the given first constituent.

    # def test_plur_er_sg_is_applicable_0(self):
    #     compound = Compound("buch_deckel")
    #     self.assertTrue(
    #         plur_er_sg_is_applicable(compound)
    #     )

    # def test_plur_er_sg_applies_0(self):
    #     compound = Compound("buch_deckel")
    #     self.assertTrue(
    #         plur_er_sg_applies(compound)
    #     )

        
    # def test_plur_er_sg_is_applicable_1(self):
    #     compound = Compound("grab_stein")
    #     self.assertTrue(
    #         plur_er_sg_is_applicable(compound)
    #     )

    # def test_plur_er_sg_applies_1(self):
    #     compound = Compound("grab_stein")
    #     self.assertTrue(
    #         plur_er_sg_applies(compound)
    #     )

        
    # def test_plur_er_sg_is_applicable_2(self):
    #     compound = Compound("blatt_fläche")
    #     self.assertTrue(
    #         plur_er_sg_is_applicable(compound)
    #     )

    # def test_plur_er_sg_applies_2(self):
    #     compound = Compound("blatt_fläche")
    #     self.assertTrue(
    #         plur_er_sg_applies(compound)
    #     )

        
    # def test_plur_er_sg_is_applicable_3(self):
    #     compound = Compound("mann_+=er_herz")
    #     self.assertTrue(
    #         plur_er_sg_is_applicable(compound)
    #     )

    # def test_plur_er_sg_applies_3(self):
    #     compound = Compound("mann_+=er_herz")
    #     self.assertFalse(
    #         plur_er_sg_applies(compound)
    #     )

        
    # def test_plur_er_sg_is_applicable_4(self):
    #     compound = Compound("kind_+=er_bild")
    #     self.assertTrue(
    #         plur_er_sg_is_applicable(compound)
    #     )

    # def test_plur_er_sg_applies_4(self):
    #     compound = Compound("kind_+=er_bild")
    #     self.assertFalse(
    #         plur_er_sg_applies(compound)
    #     )

        
    # def test_plur_er_sg_is_applicable_5(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         plur_er_sg_is_applicable(compound)
    #     )

    # def test_plur_er_sg_is_applicable_6(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         plur_er_sg_is_applicable(compound)
    #     )

	pass


class TestApplicabilityCheckersPlurErMass:

	# p2l:decl_cl:pl:#er-0/er|mass-interpr-0
	#
    # First constituents that are constituted by nouns that build
    # the plural form with -(")er
    # tend to attach a zero linker in compounds
    # in which the second constituent forces
    # a mass meaning of the given first constituent.

    # def test_plur_er_mass_is_applicable_0(self):
    #     compound = Compound("glas_auge")
    #     self.assertTrue(
    #         plur_er_mass_is_applicable(compound)
    #     )

    # def test_plur_er_mass_applies_0(self):
    #     compound = Compound("glas_auge")
    #     self.assertTrue(
    #         plur_er_mass_applies(compound)
    #     )

        
    # def test_plur_er_mass_is_applicable_1(self):
    #     compound = Compound("kraut_salat")
    #     self.assertTrue(
    #         plur_er_mass_is_applicable(compound)
    #     )

    # def test_plur_er_mass_applies_1(self):
    #     compound = Compound("kraut_salat")
    #     self.assertTrue(
    #         plur_er_mass_applies(compound)
    #     )

        
    # def test_plur_er_mass_is_applicable_2(self):
    #     compound = Compound("horn_haut")
    #     self.assertTrue(
    #         plur_er_mass_is_applicable(compound)
    #     )

    # def test_plur_er_mass_applies_2(self):
    #     compound = Compound("horn_haut")
    #     self.assertTrue(
    #         plur_er_mass_applies(compound)
    #     )

        
    # def test_plur_er_mass_is_applicable_3(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         plur_er_mass_is_applicable(compound)
    #     )

    # def test_plur_er_mass_is_applicable_4(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         plur_er_mass_is_applicable(compound)
    #     )

	pass


class TestApplicabilityCheckersPlurErPl:

	# p2l:decl_cl:pl:#er-0/er|pl_interpr-er
	#
    # First constituents that are constituted by nouns that build
    # the plural form with -(")er
    # attach -(")er- more likely in compounds
    # in which the second constituent forces
    # a plural meaning of the given first constituent.
	
    # def test_plur_er_pl_is_applicable_0(self):
    #     compound = Compound("buch_+=er_regal")
    #     self.assertTrue(
    #         plur_er_pl_is_applicable(compound)
    #     )

    # def test_plur_er_pl_applies_0(self):
    #     compound = Compound("buch_+=er_regal")
    #     self.assertTrue(
    #         plur_er_pl_applies(compound)
    #     )

        
    # def test_plur_er_pl_is_applicable_1(self):
    #     compound = Compound("grab_+=er_feld")
    #     self.assertTrue(
    #         plur_er_pl_is_applicable(compound)
    #     )

    # def test_plur_er_pl_applies_1(self):
    #     compound = Compound("grab_+=er_feld")
    #     self.assertTrue(
    #         plur_er_pl_applies(compound)
    #     )

        
    # def test_plur_er_pl_is_applicable_2(self):
    #     compound = Compound("kraut_+=er_frau")
    #     self.assertTrue(
    #         plur_er_pl_is_applicable(compound)
    #     )

    # def test_plur_er_pl_applies_2(self):
    #     compound = Compound("kraut_+=er_frau")
    #     self.assertTrue(
    #         plur_er_pl_applies(compound)
    #     )

        
    # def test_plur_er_pl_is_applicable_3(self):
    #     compound = Compound("buch_handel")
    #     self.assertTrue(
    #         plur_er_pl_is_applicable(compound)
    #     )

    # def test_plur_er_pl_applies_3(self):
    #     compound = Compound("buch_handel")
    #     self.assertFalse(
    #         plur_er_pl_applies(compound)
    #     )

        
    # def test_plur_er_pl_is_applicable_4(self):
    #     compound = Compound("bild_band")
    #     self.assertTrue(
    #         plur_er_pl_is_applicable(compound)
    #     )

    # def test_plur_er_pl_applies_4(self):
    #     compound = Compound("bild_band")
    #     self.assertFalse(
    #         plur_er_pl_applies(compound)
    #     )

        
    # def test_plur_er_pl_is_applicable_5(self):
    #     compound = Compound("kind_+=er_jacke")
    #     self.assertTrue(
    #         plur_er_pl_is_applicable(compound)
    #     )

    # def test_plur_er_pl_applies_5(self):
    #     compound = Compound("kind_+=er_jacke")
    #     self.assertFalse(
    #         plur_er_pl_applies(compound)
    #     )

        
    # def test_plur_er_pl_is_applicable_6(self):
    #     compound = Compound("mann_+=er_herz")
    #     self.assertTrue(
    #         plur_er_pl_is_applicable(compound)
    #     )

    # def test_plur_er_pl_applies_6(self):
    #     compound = Compound("mann_+=er_herz")
    #     self.assertFalse(
    #         plur_er_pl_applies(compound)
    #     )

        
    # def test_plur_er_pl_is_applicable_7(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         plur_er_pl_is_applicable(compound)
    #     )

    # def test_plur_er_pl_is_applicable_8(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         plur_er_pl_is_applicable(compound)
    #     )

	pass


class TestApplicabilityCheckersPlurErAnim:

	# p2l:decl_cl:pl:#er-0/er|anim-er
	#
    # First constituents that are constituted by
    # person and animal designations that build
    # the plural form with -(")er
    # may attach -(")er- regardless of the
    # singular/pluralinterpretation of
    # the given first constituent within the compound.

    # def test_plur_er_anim_is_applicable_0(self):
    #     compound = Compound("kind_+=er_jacke")
    #     self.assertTrue(
    #         plur_er_anim_is_applicable(compound)
    #     )

    # def test_plur_er_anim_applies_0(self):
    #     compound = Compound("kind_+=er_jacke")
    #     self.assertTrue(
    #         plur_er_anim_applies(compound)
    #     )

        
    # def test_plur_er_anim_is_applicable_1(self):
    #     compound = Compound("huhn_+=er_ei")
    #     self.assertTrue(
    #         plur_er_anim_is_applicable(compound)
    #     )

    # def test_plur_er_anim_applies_1(self):
    #     compound = Compound("huhn_+=er_ei")
    #     self.assertTrue(
    #         plur_er_anim_applies(compound)
    #     )

        
    # def test_plur_er_anim_is_applicable_2(self):
    #     compound = Compound("rind_+=er_brust")
    #     self.assertTrue(
    #         plur_er_anim_is_applicable(compound)
    #     )

    # def test_plur_er_anim_applies_2(self):
    #     compound = Compound("rind_+=er_brust")
    #     self.assertTrue(
    #         plur_er_anim_applies(compound)
    #     )

        
    # def test_plur_er_anim_is_applicable_3(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         plur_er_anim_is_applicable(compound)
    #     )

    # def test_plur_er_anim_is_applicable_4(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         plur_er_anim_is_applicable(compound)
    #     )

	pass



class TestApplicabilityCheckersPlurEUml(unittest.TestCase):
    
    # p2l:decl_cl:pl:#e_uml-0|def-0
    #
    # First constituents that are constituted by nouns that build
    # the plural form with -e and umlaut mostly have a zero linker.
        
    def test_plur_e_uml_is_applicable_0(self):
        compound = Compound("hand_fläche")
        self.assertTrue(
            plur_e_uml_is_applicable(compound)
        )

    def test_plur_e_uml_applies_0(self):
        compound = Compound("hand_fläche")
        self.assertTrue(
            plur_e_uml_applies(compound)
        )


    def test_plur_e_uml_is_applicable_1(self):
        compound = Compound("stadt_mauer")
        self.assertTrue(
            plur_e_uml_is_applicable(compound)
        )

    def test_plur_e_uml_applies_1(self):
        compound = Compound("stadt_mauer")
        self.assertTrue(
            plur_e_uml_applies(compound)
        )

    
    def test_plur_e_uml_is_applicable_2(self):
        compound = Compound("arzt_praxis")
        self.assertTrue(
            plur_e_uml_is_applicable(compound)
        )

    def test_plur_e_uml_applies_2(self):
        compound = Compound("arzt_praxis")
        self.assertTrue(
            plur_e_uml_applies(compound)
        )

    
    def test_plur_e_uml_is_applicable_3(self):
        compound = Compound("hand_+=e_druck")
        self.assertTrue(
            plur_e_uml_is_applicable(compound)
        )

    def test_plur_e_uml_applies_3(self):
        compound = Compound("hand_+=e_druck")
        self.assertFalse(
            plur_e_uml_applies(compound)
        )


    def test_plur_e_uml_is_applicable_4(self):
        compound = Compound("arzt_+=e_streik")
        self.assertTrue(
            plur_e_uml_is_applicable(compound)
        )

    def test_plur_e_uml_applies_4(self):
        compound = Compound("arzt_+=e_streik")
        self.assertFalse(
            plur_e_uml_applies(compound)
        )


    def test_plur_e_uml_is_applicable_5(self):
        compound = Compound("tag_+e_gericht")
        self.assertFalse(
            plur_e_uml_is_applicable(compound)
        )

    def test_plur_e_uml_is_applicable_6(self):
        compound = Compound("haus_tür")
        self.assertFalse(
            plur_e_uml_is_applicable(compound)
        )


class TestApplicabilityCheckersPlurEUmlPl:

	# p2l:decl_cl:pl:#e_uml-0|pl_interpr-e_uml
	#
    # First constituents that are constituted by nouns that build
    # the plural form with -e and umlaut attach -"e- irregularly in compounds
    # in which the second constituent forces
    # a plural meaning of the given first constituent.

    # def test_plur_e_uml_pl_is_applicable_0(self):
    #     compound = Compound("hand_+=e_druck")
    #     self.assertTrue(
    #         plur_e_uml_pl_is_applicable(compound)
    #     )

    # def test_plur_e_uml_pl_applies_0(self):
    #     compound = Compound("hand_+=e_druck")
    #     self.assertTrue(
    #         plur_e_uml_pl_applies(compound)
    #     )

        
    # def test_plur_e_uml_pl_is_applicable_1(self):
    #     compound = Compound("arzt_+=e_streik")
    #     self.assertTrue(
    #         plur_e_uml_pl_is_applicable(compound)
    #     )

    # def test_plur_e_uml_pl_applies_1(self):
    #     compound = Compound("arzt_+=e_streik")
    #     self.assertTrue(
    #         plur_e_uml_pl_applies(compound)
    #     )

        
    # def test_plur_e_uml_pl_is_applicable_2(self):
    #     compound = Compound("gast_+=e_buch")
    #     self.assertTrue(
    #         plur_e_uml_pl_is_applicable(compound)
    #     )

    # def test_plur_e_uml_pl_applies_2(self):
    #     compound = Compound("gast_+=e_buch")
    #     self.assertTrue(
    #         plur_e_uml_pl_applies(compound)
    #     )

        
    # def test_plur_e_uml_pl_is_applicable_3(self):
    #     compound = Compound("baum_gruppe")
    #     self.assertTrue(
    #         plur_e_uml_pl_is_applicable(compound)
    #     )

    # def test_plur_e_uml_pl_applies_3(self):
    #     compound = Compound("baum_gruppe")
    #     self.assertFalse(
    #         plur_e_uml_pl_applies(compound)
    #     )

        
    # def test_plur_e_uml_pl_is_applicable_4(self):
    #     compound = Compound("zug_verkehr")
    #     self.assertTrue(
    #         plur_e_uml_pl_is_applicable(compound)
    #     )

    # def test_plur_e_uml_pl_applies_4(self):
    #     compound = Compound("zug_verkehr")
    #     self.assertFalse(
    #         plur_e_uml_pl_applies(compound)
    #     )

        
    # def test_plur_e_uml_pl_is_applicable_5(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         plur_e_uml_pl_is_applicable(compound)
    #     )

    # def test_plur_e_uml_pl_is_applicable_6(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         plur_e_uml_pl_is_applicable(compound)
    #     )

	pass



class TestApplicabilityCheckersPlur0Uml(unittest.TestCase):
    
    # p2l:decl_cl:pl:#0_uml-0|def-0
    #
    # First constituents that are constituted by nouns that build
    # the plural form with a zero ending and umlaut mostly have a zero linker.
            
    def test_plur_0_uml_is_applicable_0(self):
        compound = Compound("apfel_baum")
        self.assertTrue(
            plur_0_uml_is_applicable(compound)
        )

    def test_plur_0_uml_applies_0(self):
        compound = Compound("apfel_baum")
        self.assertTrue(
            plur_0_uml_applies(compound)
        )


    def test_plur_0_uml_is_applicable_1(self):
        compound = Compound("kloster_kirche")
        self.assertTrue(
            plur_0_uml_is_applicable(compound)
        )

    def test_plur_0_uml_applies_1(self):
        compound = Compound("kloster_kirche")
        self.assertTrue(
            plur_0_uml_applies(compound)
        )

    
    def test_plur_0_uml_is_applicable_2(self):
        compound = Compound("mutter_sprache")
        self.assertTrue(
            plur_0_uml_is_applicable(compound)
        )

    def test_plur_0_uml_applies_2(self):
        compound = Compound("mutter_sprache")
        self.assertTrue(
            plur_0_uml_applies(compound)
        )

    
    def test_plur_0_uml_is_applicable_3(self):
        compound = Compound("bruder_+=_gemeinde")
        self.assertTrue(
            plur_0_uml_is_applicable(compound)
        )

    def test_plur_0_uml_applies_3(self):
        compound = Compound("bruder_+=_gemeinde")
        self.assertFalse(
            plur_0_uml_applies(compound)
        )


    def test_plur_0_uml_is_applicable_4(self):
        compound = Compound("mutter_+=_zentrum")
        self.assertTrue(
            plur_0_uml_is_applicable(compound)
        )

    def test_plur_0_uml_applies_4(self):
        compound = Compound("mutter_+=_zentrum")
        self.assertFalse(
            plur_0_uml_applies(compound)
        )


    def test_plur_0_uml_is_applicable_5(self):
        compound = Compound("tag_+e_gericht")
        self.assertFalse(
            plur_0_uml_is_applicable(compound)
        )

    def test_plur_0_uml_is_applicable_6(self):
        compound = Compound("haus_tür")
        self.assertFalse(
            plur_0_uml_is_applicable(compound)
        )


class TestApplicabilityCheckersPlur0UmlPl:

	# p2l:decl_cl:pl:#0_uml-0|pl_interpr-0_uml
	#
    # First constituents that are constituted by nouns that build
    # the plural form with a zero ending and umlaut attach
    # a zero linker with umlaut irregularly in compounds
    # in which the second constituent forces
    # a plural meaning of the given first constituent.

    # def test_plur_0_uml_pl_applies_0(self):
    #     compound = Compound("bruder_+=_gemeinde")
    #     self.assertTrue(
    #         plur_0_uml_pl_applies(compound)
    #     )

        
    # def test_plur_0_uml_pl_is_applicable_1(self):
    #     compound = Compound("mutter_+=_zentrum")
    #     self.assertTrue(
    #         plur_0_uml_pl_is_applicable(compound)
    #     )

    # def test_plur_0_uml_pl_applies_1(self):
    #     compound = Compound("mutter_+=_zentrum")
    #     self.assertTrue(
    #         plur_0_uml_pl_applies(compound)
    #     )

        
    # def test_plur_0_uml_pl_is_applicable_2(self):
    #     compound = Compound("vater_+=_aufbruch")
    #     self.assertTrue(
    #         plur_0_uml_pl_is_applicable(compound)
    #     )

    # def test_plur_0_uml_pl_applies_2(self):
    #     compound = Compound("vater_+=_aufbruch")
    #     self.assertTrue(
    #         plur_0_uml_pl_applies(compound)
    #     )

        
    # def test_plur_0_uml_pl_is_applicable_3(self):
    #     compound = Compound("vogel_futter")
    #     self.assertTrue(
    #         plur_0_uml_pl_is_applicable(compound)
    #     )

    # def test_plur_0_uml_pl_applies_3(self):
    #     compound = Compound("vogel_futter")
    #     self.assertFalse(
    #         plur_0_uml_pl_applies(compound)
    #     )

        
    # def test_plur_0_uml_pl_is_applicable_4(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         plur_0_uml_pl_is_applicable(compound)
    #     )

    # def test_plur_0_uml_pl_is_applicable_5(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         plur_0_uml_pl_is_applicable(compound)
    #     )

	pass



class TestApplicabilityCheckersMixedMN(unittest.TestCase):
    
    # p2l:decl_cl:mixed-0/s/en|def-0/s/en
    #
    # First constituents that are constituted by
    # mixed masculine and neuter nouns
    # almost always attach -s-, a zero linker, or -(e)n-.
            
    def test_mixed_mn_is_applicable_0(self):
        compound = Compound("staat_+s_amt")
        self.assertTrue(
            mixed_mn_is_applicable(compound)
        )

    def test_mixed_mn_applies_0(self):
        compound = Compound("staat_+s_amt")
        self.assertTrue(
            mixed_mn_applies(compound)
        )


    def test_mixed_mn_is_applicable_1(self):
        compound = Compound("staat_+en_bund")
        self.assertTrue(
            mixed_mn_is_applicable(compound)
        )

    def test_mixed_mn_applies_1(self):
        compound = Compound("staat_+en_bund")
        self.assertTrue(
            mixed_mn_applies(compound)
        )

    
    def test_mixed_mn_is_applicable_2(self):
        compound = Compound("bett_anzug")
        self.assertTrue(
            mixed_mn_is_applicable(compound)
        )

    def test_mixed_mn_applies_2(self):
        compound = Compound("bett_anzug")
        self.assertTrue(
            mixed_mn_applies(compound)
        )

    
    def test_mixed_mn_is_applicable_3(self):
        compound = Compound("auge_+n_lied")
        self.assertTrue(
            mixed_mn_is_applicable(compound)
        )

    def test_mixed_mn_applies_3(self):
        compound = Compound("auge_+n_lied")
        self.assertTrue(
            mixed_mn_applies(compound)
        )


    def test_mixed_mn_is_applicable_4(self):
        compound = Compound("tag_+e_gericht")
        self.assertFalse(
            mixed_mn_is_applicable(compound)
        )

    def test_mixed_mn_is_applicable_5(self):
        compound = Compound("haus_tür")
        self.assertFalse(
            mixed_mn_is_applicable(compound)
        )


class TestApplicabilityCheckersMixedMnPl:

	# p2l:decl_cl:mixed-0/s/en|pl_interpr-en
	#
    # First constituents that are constituted by
    # mixed masculine and neuter nouns attach -(e)n-more likely in compounds
    # in which the second constituent forces
    # a plural meaning of the given first constituent..

    # def test_mixed_mn_pl_is_applicable_0(self):
    #     compound = Compound("staat_+en_bund")
    #     self.assertTrue(
    #         mixed_mn_pl_is_applicable(compound)
    #     )

    # def test_mixed_mn_pl_applies_0(self):
    #     compound = Compound("staat_+en_bund")
    #     self.assertTrue(
    #         mixed_mn_pl_applies(compound)
    #     )

        
    # def test_mixed_mn_pl_is_applicable_1(self):
    #     compound = Compound("bett_+en_zahl")
    #     self.assertTrue(
    #         mixed_mn_pl_is_applicable(compound)
    #     )

    # def test_mixed_mn_pl_applies_1(self):
    #     compound = Compound("bett_+en_zahl")
    #     self.assertTrue(
    #         mixed_mn_pl_applies(compound)
    #     )

        
    # def test_mixed_mn_pl_is_applicable_2(self):
    #     compound = Compound("strahl_+en_belastung")
    #     self.assertTrue(
    #         mixed_mn_pl_is_applicable(compound)
    #     )

    # def test_mixed_mn_pl_applies_2(self):
    #     compound = Compound("strahl_+en_belastung")
    #     self.assertTrue(
    #         mixed_mn_pl_applies(compound)
    #     )

        
    # def test_mixed_mn_pl_is_applicable_3(self):
    #     compound = Compound("motor_+en_geräusch")
    #     self.assertTrue(
    #         mixed_mn_pl_is_applicable(compound)
    #     )

    # def test_mixed_mn_pl_applies_3(self):
    #     compound = Compound("motor_+en_geräusch")
    #     self.assertFalse(
    #         mixed_mn_pl_applies(compound)
    #     )

        
    # def test_mixed_mn_pl_is_applicable_4(self):
    #     compound = Compound("professor_+en_titel")
    #     self.assertTrue(
    #         mixed_mn_pl_is_applicable(compound)
    #     )

    # def test_mixed_mn_pl_applies_4(self):
    #     compound = Compound("professor_+en_titel")
    #     self.assertFalse(
    #         mixed_mn_pl_applies(compound)
    #     )

        
    # def test_mixed_mn_pl_is_applicable_5(self):
    #     compound = Compound("auge_+n_lied")
    #     self.assertTrue(
    #         mixed_mn_pl_is_applicable(compound)
    #     )

    # def test_mixed_mn_pl_applies_5(self):
    #     compound = Compound("auge_+n_lied")
    #     self.assertFalse(
    #         mixed_mn_pl_applies(compound)
    #     )

        
    # def test_mixed_mn_pl_is_applicable_6(self):
    #     compound = Compound("interesse_+n_bereich")
    #     self.assertTrue(
    #         mixed_mn_pl_is_applicable(compound)
    #     )

    # def test_mixed_mn_pl_applies_6(self):
    #     compound = Compound("interesse_+n_bereich")
    #     self.assertFalse(
    #         mixed_mn_pl_applies(compound)
    #     )

        
    # def test_mixed_mn_pl_is_applicable_7(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         mixed_mn_pl_is_applicable(compound)
    #     )

    # def test_mixed_mn_pl_is_applicable_8(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         mixed_mn_pl_is_applicable(compound)
    #     )

	pass



class TestApplicabilityCheckersSfxPl0(unittest.TestCase):
    
    # p2l:drv:sfx:0_pl_sfx-0
    #
    # First constituents that are constituted by derived nouns with suffixes
    # -er, -ler, -ner, -el, -sel, -chen, -lein that build the plural form
    # with a zero ending attach a zero linking element regularly.
            
    def test_sfx_pl_0_is_applicable_0(self):
        compound = Compound("reiter_schwert")
        self.assertTrue(
            sfx_pl_0_is_applicable(compound)
        )

    def test_sfx_pl_0_applies_0(self):
        compound = Compound("reiter_schwert")
        self.assertTrue(
            sfx_pl_0_applies(compound)
        )


    def test_sfx_pl_0_is_applicable_1(self):
        compound = Compound("gürtel_schnalle")
        self.assertTrue(
            sfx_pl_0_is_applicable(compound)
        )

    def test_sfx_pl_0_applies_1(self):
        compound = Compound("gürtel_schnalle")
        self.assertTrue(
            sfx_pl_0_applies(compound)
        )

    
    def test_sfx_pl_0_is_applicable_2(self):
        compound = Compound("brötchen_geber")
        self.assertTrue(
            sfx_pl_0_is_applicable(compound)
        )

    def test_sfx_pl_0_applies_2(self):
        compound = Compound("brötchen_geber")
        self.assertTrue(
            sfx_pl_0_applies(compound)
        )


    def test_sfx_pl_0_is_applicable_3(self):
        compound = Compound("alter_+s_abstand")
        self.assertTrue(
            sfx_pl_0_is_applicable(compound)
        )

    def test_sfx_pl_0_applies_3(self):
        compound = Compound("alter_+s_abstand")
        self.assertFalse(
            sfx_pl_0_applies(compound)
        )

    
    def test_sfx_pl_0_is_applicable_4(self):
        compound = Compound("reiter_+s_mann")
        self.assertTrue(
            sfx_pl_0_is_applicable(compound)
        )

    def test_sfx_pl_0_applies_4(self):
        compound = Compound("reiter_+s_mann")
        self.assertFalse(
            sfx_pl_0_applies(compound)
        )


    def test_sfx_pl_0_is_applicable_5(self):
        compound = Compound("mutter_sprache")
        self.assertFalse(
            sfx_pl_0_is_applicable(compound)
        )

    def test_sfx_pl_0_is_applicable_6(self):
        compound = Compound("teufel_+s_werk")
        self.assertFalse(
            sfx_pl_0_is_applicable(compound)
        )



class TestApplicabilityCheckersSfxPlE(unittest.TestCase):

	# p2l:drv:sfx:e_pl_sfx-0
	#
    # First constituents that are constituted by derived nouns with suffixes
    # -bold, -nis, -rich, -at, -al that build
    # the plural form with -e attach a zero linker regularly..

    def test_sfx_pl_e_is_applicable_0(self):
        compound = Compound("erlaubnis_schein")
        self.assertTrue(
            sfx_pl_e_is_applicable(compound)
        )

    def test_sfx_pl_e_applies_0(self):
        compound = Compound("erlaubnis_schein")
        self.assertTrue(
            sfx_pl_e_applies(compound)
        )

        
    def test_sfx_pl_e_is_applicable_1(self):
        compound = Compound("format_vorlage")
        self.assertTrue(
            sfx_pl_e_is_applicable(compound)
        )

    def test_sfx_pl_e_applies_1(self):
        compound = Compound("format_vorlage")
        self.assertTrue(
            sfx_pl_e_applies(compound)
        )

        
    def test_sfx_pl_e_is_applicable_2(self):
        compound = Compound("personal_ausweis")
        self.assertTrue(
            sfx_pl_e_is_applicable(compound)
        )

    def test_sfx_pl_e_applies_2(self):
        compound = Compound("personal_ausweis")
        self.assertTrue(
            sfx_pl_e_applies(compound)
        )


    def test_sfx_pl_e_is_applicable_3(self):
        compound = Compound("radikal_+e_fänger")
        self.assertTrue(
            sfx_pl_e_is_applicable(compound)
        )

    def test_sfx_pl_e_applies_3(self):
        compound = Compound("radikal_+e_fänger")
        self.assertFalse(
            sfx_pl_e_applies(compound)
        )

        
    def test_sfx_pl_e_is_applicable_4(self):
        compound = Compound("brötchen_geber")
        self.assertFalse(
            sfx_pl_e_is_applicable(compound)
        )

    def test_sfx_pl_e_is_applicable_5(self):
        compound = Compound("reiter_schwert")
        self.assertFalse(
            sfx_pl_e_is_applicable(compound)
        )


    def test_sfx_pl_e_is_applicable_corr_0(self):
        compound = Compound("format_vorlage")
        self.assertFalse(
            sfx_pl_e_is_applicable_corr(compound)
        )

    def test_sfx_pl_e_is_applicable_corr_1(self):
        compound = Compound("dekanat_+s_leitung")
        self.assertFalse(
            sfx_pl_e_is_applicable_corr(compound)
        )



class TestApplicabilityCheckersSchwaFinDeverb(unittest.TestCase):

	# p2l:drv:deverb_schwa$-0|def-0
	#
    # First constituents that are constituted by deverbal feminine nouns
    # with a schwa suffix mostly attach a zero linker.

    def test_schwa_fin_deverb_is_applicable_0(self):
        compound = Compound("abgabe_soll")
        self.assertTrue(
            schwa_fin_deverb_is_applicable(compound)
        )

    def test_schwa_fin_deverb_applies_0(self):
        compound = Compound("abgabe_soll")
        self.assertTrue(
            schwa_fin_deverb_applies(compound)
        )

        
    # def test_schwa_fin_deverb_is_applicable_1(self):
    #     compound = Compound("vorsorge_pflicht")    # 'Sorge' is simplex N in CELEX
    #     self.assertTrue(
    #         schwa_fin_deverb_is_applicable(compound)
    #     )

    # def test_schwa_fin_deverb_applies_1(self):
    #     compound = Compound("vorsorge_pflicht")
    #     self.assertTrue(
    #         schwa_fin_deverb_applies(compound)
    #     )

        
    def test_schwa_fin_deverb_is_applicable_2(self):
        compound = Compound("ablage_fach")  # 'Lage' is simplex N in CELEX
        self.assertTrue(
            schwa_fin_deverb_is_applicable(compound)
        )

    def test_schwa_fin_deverb_applies_2(self):
        compound = Compound("ablage_fach")
        self.assertTrue(
            schwa_fin_deverb_applies(compound)
        )

        
    def test_schwa_fin_deverb_is_applicable_3(self):
        compound = Compound("abgabe_+n_ordnung")
        self.assertTrue(
            schwa_fin_deverb_is_applicable(compound)
        )

    def test_schwa_fin_deverb_applies_3(self):
        compound = Compound("abgabe_+n_ordnung")
        self.assertFalse(
            schwa_fin_deverb_applies(compound)
        )

        
    def test_schwa_fin_deverb_is_applicable_4(self):
        compound = Compound("anzeige_+n_blatt")
        self.assertTrue(
            schwa_fin_deverb_is_applicable(compound)
        )

    def test_schwa_fin_deverb_applies_4(self):
        compound = Compound("anzeige_+n_blatt")
        self.assertFalse(
            schwa_fin_deverb_applies(compound)
        )

        
    def test_schwa_fin_deverb_is_applicable_5(self):
        compound = Compound("lüge_+n_detektor")
        self.assertTrue(
            schwa_fin_deverb_is_applicable(compound)
        )

    def test_schwa_fin_deverb_applies_5(self):
        compound = Compound("lüge_+n_detektor")
        self.assertFalse(
            schwa_fin_deverb_applies(compound)
        )

        
    def test_schwa_fin_deverb_is_applicable_6(self):
        compound = Compound("blume_+n_topf")
        self.assertFalse(
            schwa_fin_deverb_is_applicable(compound)
        )

    def test_schwa_fin_deverb_is_applicable_7(self):
        compound = Compound("fläche_maß")
        self.assertFalse(
            schwa_fin_deverb_is_applicable(compound)
        )


class TestApplicabilityCheckersSchwaFinDeverbPl:

	# p2l:drv:deverb_schwa$-0|pl_interpr-en
	#
    # First constituents that are constituted by deverbal feminine nouns
    # with a schwa suffix tend to attach -n- in compoundsin which the second
    # constituent forces a plural reading of the given first constituent.

    # def test_schwa_fin_deverb_pl_is_applicable_0(self):
    #     compound = Compound("abgabe_+n_ordnung")
    #     self.assertTrue(
    #         schwa_fin_deverb_pl_is_applicable(compound)
    #     )

    # def test_schwa_fin_deverb_pl_applies_0(self):
    #     compound = Compound("abgabe_+n_ordnung")
    #     self.assertTrue(
    #         schwa_fin_deverb_pl_applies(compound)
    #     )

        
    # def test_schwa_fin_deverb_pl_is_applicable_1(self):
    #     compound = Compound("anzeige_+n_blatt")
    #     self.assertTrue(
    #         schwa_fin_deverb_pl_is_applicable(compound)
    #     )

    # def test_schwa_fin_deverb_pl_applies_1(self):
    #     compound = Compound("anzeige_+n_blatt")
    #     self.assertTrue(
    #         schwa_fin_deverb_pl_applies(compound)
    #     )

        
    # def test_schwa_fin_deverb_pl_is_applicable_2(self):
    #     compound = Compound("lüge_+n_detektor")
    #     self.assertTrue(
    #         schwa_fin_deverb_pl_is_applicable(compound)
    #     )

    # def test_schwa_fin_deverb_pl_applies_2(self):
    #     compound = Compound("lüge_+n_detektor")
    #     self.assertTrue(
    #         schwa_fin_deverb_pl_applies(compound)
    #     )

        
    # def test_schwa_fin_deverb_pl_is_applicable_3(self):
    #     compound = Compound("einnahme_buch")
    #     self.assertTrue(
    #         schwa_fin_deverb_pl_is_applicable(compound)
    #     )

    # def test_schwa_fin_deverb_pl_applies_3(self):
    #     compound = Compound("einnahme_buch")
    #     self.assertFalse(
    #         schwa_fin_deverb_pl_applies(compound)
    #     )

        
    # def test_schwa_fin_deverb_pl_is_applicable_4(self):
    #     compound = Compound("anzeige_tafel")
    #     self.assertTrue(
    #         schwa_fin_deverb_pl_is_applicable(compound)
    #     )

    # def test_schwa_fin_deverb_pl_applies_4(self):
    #     compound = Compound("anzeige_tafel")
    #     self.assertFalse(
    #         schwa_fin_deverb_pl_applies(compound)
    #     )

        
    # def test_schwa_fin_deverb_pl_is_applicable_5(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         schwa_fin_deverb_pl_is_applicable(compound)
    #     )

    # def test_schwa_fin_deverb_pl_is_applicable_6(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         schwa_fin_deverb_pl_is_applicable(compound)
    #     )

	pass



class TestApplicabilityCheckersSchwaFinDeadj(unittest.TestCase):

	# p2l:drv:deadj_schwa$-0/en
	#
    # First constituents that are constituted by deadjectival feminine nouns
    # with a schwa suffix almost always attach -n- or a zero linker.
    # Each of the two linkers is preferred in about the same number of cases.

    def test_schwa_fin_deadj_is_applicable_0(self):
        compound = Compound("fläche_maß")
        self.assertTrue(
            schwa_fin_deadj_is_applicable(compound)
        )

    def test_schwa_fin_deadj_applies_0(self):
        compound = Compound("fläche_maß")
        self.assertTrue(
            schwa_fin_deadj_applies(compound)
        )

        
    def test_schwa_fin_deadj_is_applicable_1(self):
        compound = Compound("grüne_wald")
        self.assertTrue(
            schwa_fin_deadj_is_applicable(compound)
        )

    def test_schwa_fin_deadj_applies_1(self):
        compound = Compound("grüne_wald")
        self.assertTrue(
            schwa_fin_deadj_applies(compound)
        )

        
    def test_schwa_fin_deadj_is_applicable_2(self):
        compound = Compound("tiefe_+n_meter")
        self.assertTrue(
            schwa_fin_deadj_is_applicable(compound)
        )

    def test_schwa_fin_deadj_applies_2(self):
        compound = Compound("tiefe_+n_meter")
        self.assertTrue(
            schwa_fin_deadj_applies(compound)
        )

    
    def test_schwa_fin_deadj_is_applicable_3(self):
        compound = Compound("größe_+n_klasse")
        self.assertTrue(
            schwa_fin_deadj_is_applicable(compound)
        )

    def test_schwa_fin_deadj_applies_3(self):
        compound = Compound("größe_+n_klasse")
        self.assertTrue(
            schwa_fin_deadj_applies(compound)
        )

        
    def test_schwa_fin_deadj_is_applicable_4(self):
        compound = Compound("blume_+n_topf")
        self.assertFalse(
            schwa_fin_deadj_is_applicable(compound)
        )

    def test_schwa_fin_deadj_is_applicable_5(self):
        compound = Compound("analogie_effekt")
        self.assertFalse(
            schwa_fin_deadj_is_applicable(compound)
        )



class TestApplicabilityCheckersSfxS(unittest.TestCase):

	# p2l:drv:sfx:sfx-s|def-s
	#
    # First constituents that are constituted by derived nouns with suffixes
    # -(ig)keit, -heit, -schaft, -ung, -sal, -ing, -ling, -tum, -um, -ion,
    # also -ität and its allomorphs attach -s- regularly.

    def test_sfx_s_is_applicable_0(self):
        compound = Compound("gesundheit_+s_amt")
        self.assertTrue(
            sfx_s_is_applicable(compound)
        )

    def test_sfx_s_applies_0(self):
        compound = Compound("gesundheit_+s_amt")
        self.assertTrue(
            sfx_s_applies(compound)
        )

        
    def test_sfx_s_is_applicable_1(self):
        compound = Compound("gesellschaft_+s_politik")
        self.assertTrue(
            sfx_s_is_applicable(compound)
        )

    def test_sfx_s_applies_1(self):
        compound = Compound("gesellschaft_+s_politik")
        self.assertTrue(
            sfx_s_applies(compound)
        )

        
    def test_sfx_s_is_applicable_2(self):
        compound = Compound("schicksal_+s_drama")
        self.assertTrue(
            sfx_s_is_applicable(compound)
        )

    def test_sfx_s_applies_2(self):
        compound = Compound("schicksal_+s_drama")
        self.assertTrue(
            sfx_s_applies(compound)
        )

        
    def test_sfx_s_is_applicable_3(self):
        compound = Compound("rarität_+s_wert")
        self.assertTrue(
            sfx_s_is_applicable(compound)
        )

    def test_sfx_s_applies_3(self):
        compound = Compound("rarität_+s_wert")
        self.assertTrue(
            sfx_s_applies(compound)
        )

        
    def test_sfx_s_is_applicable_4(self):
        compound = Compound("eigentum_+s_recht")
        self.assertTrue(
            sfx_s_is_applicable(compound)
        )

    def test_sfx_s_applies_4(self):
        compound = Compound("eigentum_+s_recht")
        self.assertTrue(
            sfx_s_applies(compound)
        )

        
    def test_sfx_s_is_applicable_5(self):
        compound = Compound("minderheit_+en_recht")
        self.assertTrue(
            sfx_s_is_applicable(compound)
        )

    def test_sfx_s_applies_5(self):
        compound = Compound("minderheit_+en_recht")
        self.assertFalse(
            sfx_s_applies(compound)
        )

        
    def test_sfx_s_is_applicable_6(self):
        compound = Compound("visum_antrag")
        self.assertFalse(
            sfx_s_is_applicable(compound)
        )

    def test_sfx_s_is_applicable_7(self):
        compound = Compound("ding_+=er_mann")
        self.assertFalse(
            sfx_s_is_applicable(compound)
        )


class TestApplicabilityCheckersSfxItaetPl:

	# p2l:drv:sfx:sfx-s|#itaet$_pl_interpr-en
	#
    # First constituents that are constituted by derived nouns with suffix
    # -ität and its allomorphs prefer -en- in compounds in which the second
    # constituent forces a plural meaning of the given first constituent.

    # def test_sfx_itaet_pl_is_applicable_0(self):
    #     compound = Compound("rarität_+en_sammlung")
    #     self.assertTrue(
    #         sfx_itaet_pl_is_applicable(compound)
    #     )

    # def test_sfx_itaet_pl_applies_0(self):
    #     compound = Compound("rarität_+en_sammlung")
    #     self.assertTrue(
    #         sfx_itaet_pl_applies(compound)
    #     )

        
    # def test_sfx_itaet_pl_is_applicable_1(self):
    #     compound = Compound("kuriosität_+en_händler")
    #     self.assertTrue(
    #         sfx_itaet_pl_is_applicable(compound)
    #     )

    # def test_sfx_itaet_pl_applies_1(self):
    #     compound = Compound("kuriosität_+en_händler")
    #     self.assertTrue(
    #         sfx_itaet_pl_applies(compound)
    #     )

        
    # def test_sfx_itaet_pl_is_applicable_2(self):
    #     compound = Compound("aktualitäten_+en_kino")
    #     self.assertTrue(
    #         sfx_itaet_pl_is_applicable(compound)
    #     )

    # def test_sfx_itaet_pl_applies_2(self):
    #     compound = Compound("aktualitäten_+en_kino")
    #     self.assertTrue(
    #         sfx_itaet_pl_applies(compound)
    #     )

        
    # def test_sfx_itaet_pl_is_applicable_3(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         sfx_itaet_pl_is_applicable(compound)
    #     )

    # def test_sfx_itaet_pl_is_applicable_4(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         sfx_itaet_pl_is_applicable(compound)
    #     )

	pass



class TestApplicabilityCheckersSfxDeverbEn(unittest.TestCase):

	# p2l:drv:sfx:deverb_#en$-s
	#
    # First constituents that are constituted by deverbal nouns
    # that end in suffix -en attach -s- regularly.

    def test_sfx_deverb_en_is_applicable_0(self):
        compound = Compound("leben_+s_mittel")
        self.assertTrue(
            sfx_deverb_en_is_applicable(compound)
        )

    def test_sfx_deverb_en_applies_0(self):
        compound = Compound("leben_+s_mittel")
        self.assertTrue(
            sfx_deverb_en_applies(compound)
        )

        
    def test_sfx_deverb_en_is_applicable_1(self):
        compound = Compound("essen_+s_gewohnheit")
        self.assertTrue(
            sfx_deverb_en_is_applicable(compound)
        )

    def test_sfx_deverb_en_applies_1(self):
        compound = Compound("essen_+s_gewohnheit")
        self.assertTrue(
            sfx_deverb_en_applies(compound)
        )

        
    def test_sfx_deverb_en_is_applicable_2(self):
        compound = Compound("unternehmen_+s_bereich")
        self.assertTrue(
            sfx_deverb_en_is_applicable(compound)
        )

    def test_sfx_deverb_en_applies_2(self):
        compound = Compound("unternehmen_+s_bereich")
        self.assertTrue(
            sfx_deverb_en_applies(compound)
        )

        
    def test_sfx_deverb_en_is_applicable_3(self):
        compound = Compound("liebe_+s_brief")
        self.assertFalse(
            sfx_deverb_en_is_applicable(compound)
        )

    def test_sfx_deverb_en_is_applicable_4(self):
        compound = Compound("alter_vorsorge")
        self.assertFalse(
            sfx_deverb_en_is_applicable(compound)
        )


    def test_sfx_deverb_en_is_applicable_corr_0(self):
        compound = Compound("leben_stil")
        self.assertTrue(
            sfx_deverb_en_is_applicable_corr(compound)
        )

    def test_sfx_deverb_en_applies_corr_0(self):
        compound = Compound("leben_stil")
        self.assertTrue(
            sfx_deverb_en_applies_corr(compound)
        )


    def test_sfx_deverb_en_is_applicable_corr_1(self):
        compound = Compound("essen_geruch")
        self.assertTrue(
            sfx_deverb_en_is_applicable_corr(compound)
        )

    def test_sfx_deverb_en_applies_corr_1(self):
        compound = Compound("essen_geruch")
        self.assertTrue(
            sfx_deverb_en_applies_corr(compound)
        )



class TestApplicabilityCheckersSfxFInEn(unittest.TestCase):

	# p2l:drv:sfx:F_#in$-en
	#
    # First constituents that are constituted by derived feminine nouns
    # with suffix -in always attach -en-.
    # (The suffix -in adjusts orthographically in this case and becomes -inn.)

    def test_sfx_F_in_en_is_applicable_0(self):
        compound = Compound("lehrerinn_+en_mentalität")
        self.assertTrue(
            sfx_F_in_en_is_applicable(compound)
        )

    def test_sfx_F_in_en_applies_0(self):
        compound = Compound("lehrehrinn_+en_mentalität")
        self.assertTrue(
            sfx_F_in_en_applies(compound)
        )

        
    def test_sfx_F_in_en_is_applicable_1(self):
        compound = Compound("freundinn_+en_gruppe")
        self.assertTrue(
            sfx_F_in_en_is_applicable(compound)
        )

    def test_sfx_F_in_en_applies_1(self):
        compound = Compound("freundinn_+en_gruppe")
        self.assertTrue(
            sfx_F_in_en_applies(compound)
        )

        
    def test_sfx_F_in_en_is_applicable_2(self):
        compound = Compound("schülerinn_+en_rat")
        self.assertTrue(
            sfx_F_in_en_is_applicable(compound)
        )

    def test_sfx_F_in_en_applies_2(self):
        compound = Compound("schülerinn_+en_rat")
        self.assertTrue(
            sfx_F_in_en_applies(compound)
        )

        
    def test_sfx_F_in_en_is_applicable_3(self):
        compound = Compound("königin_mutter")
        self.assertTrue(
            sfx_F_in_en_is_applicable(compound)
        )

    def test_sfx_F_in_en_applies_3(self):
        compound = Compound("königin_mutter")
        self.assertFalse(
            sfx_F_in_en_applies(compound)
        )

        
    def test_sfx_F_in_en_is_applicable_4(self):
        compound = Compound("wein_schorle")
        self.assertFalse(
            sfx_F_in_en_is_applicable(compound)
        )

    def test_sfx_F_in_en_is_applicable_5(self):
        compound = Compound("bein_bruch")
        self.assertFalse(
            sfx_F_in_en_is_applicable(compound)
        )



class TestApplicabilityCheckersPrxDeverb(unittest.TestCase):

	# p2l:drv:prx_deverb-s
	#
    # First constituents that are constituted by prefixed deverbal nouns
    # exhibit a strong tendency to attach -s-.
     
    def test_prx_deverb_is_applicable_0(self):
        compound = Compound("anspruch_+s_haltung")
        self.assertTrue(
            prx_deverb_is_applicable(compound)
        )

    def test_prx_deverb_applies_0(self):
        compound = Compound("anspruch_+s_haltung")
        self.assertTrue(
            prx_deverb_applies(compound)
        )

        
    def test_prx_deverb_is_applicable_1(self):
        compound = Compound("eintrag_+s_frist")
        self.assertTrue(
            prx_deverb_is_applicable(compound)
        )

    def test_prx_deverb_applies_1(self):
        compound = Compound("eintrag_+s_frist")
        self.assertTrue(
            prx_deverb_applies(compound)
        )

        
    def test_prx_deverb_is_applicable_2(self):
        compound = Compound("bedarf_+s_fall")
        self.assertTrue(
            prx_deverb_is_applicable(compound)
        )

    def test_prx_deverb_applies_2(self):
        compound = Compound("bedarf_+s_fall")
        self.assertTrue(
            prx_deverb_applies(compound)
        )

        
    def test_prx_deverb_is_applicable_3(self):
        compound = Compound("verfall_+s_datum")
        self.assertTrue(
            prx_deverb_is_applicable(compound)
        )

    def test_prx_deverb_applies_3(self):
        compound = Compound("verfall_+s_datum")
        self.assertTrue(
            prx_deverb_applies(compound)
        )

        
    def test_prx_deverb_is_applicable_4(self):
        compound = Compound("anruf_beantworter")
        self.assertTrue(
            prx_deverb_is_applicable(compound)
        )

    def test_prx_deverb_applies_4(self):
        compound = Compound("anruf_beantworter")
        self.assertFalse(
            prx_deverb_applies(compound)
        )

        
    def test_prx_deverb_is_applicable_5(self):
        compound = Compound("überfall_kommando")
        self.assertTrue(
            prx_deverb_is_applicable(compound)
        )

    def test_prx_deverb_applies_5(self):
        compound = Compound("überfall_kommando")
        self.assertFalse(
            prx_deverb_applies(compound)
        )

        
    # def test_prx_deverb_is_applicable_6(self):
    #     compound = Compound("bestand_teil")   # not prefixed in CELEX
    #     self.assertTrue(
    #         prx_deverb_is_applicable(compound)
    #     )

    # def test_prx_deverb_applies_6(self):
    #     compound = Compound("bestand_teil")
    #     self.assertFalse(
    #         prx_deverb_applies(compound)
    #     )

        
    def test_prx_deverb_is_applicable_7(self):
        compound = Compound("abend_essen")
        self.assertFalse(
            prx_deverb_is_applicable(compound)
        )

    def test_prx_deverb_is_applicable_8(self):
        compound = Compound("version_+s_geschichte")
        self.assertFalse(
            prx_deverb_is_applicable(compound)
        )



class TestApplicabilityCheckersSibilantFin(unittest.TestCase):

	# p2l:phon_fin:sibilant$-0
	#
    # First constituents that are constituted by nouns that endin a sibilant
    # or in a consonant cluster including [s] mostly adopt a zero linker.

    def test_sibilant_fin_is_applicable_0(self):
        compound = Compound("gefäß_system")
        self.assertTrue(
            sibilant_fin_is_applicable(compound)
        )

    def test_sibilant_fin_applies_0(self):
        compound = Compound("gefäß_system")
        self.assertTrue(
            sibilant_fin_applies(compound)
        )

        
    def test_sibilant_fin_is_applicable_1(self):
        compound = Compound("fisch_öl")
        self.assertTrue(
            sibilant_fin_is_applicable(compound)
        )

    def test_sibilant_fin_applies_1(self):
        compound = Compound("fisch_öl")
        self.assertTrue(
            sibilant_fin_applies(compound)
        )

        
    def test_sibilant_fin_is_applicable_2(self):
        compound = Compound("notiz_buch")
        self.assertTrue(
            sibilant_fin_is_applicable(compound)
        )

    def test_sibilant_fin_applies_2(self):
        compound = Compound("notiz_buch")
        self.assertTrue(
            sibilant_fin_applies(compound)
        )

        
    def test_sibilant_fin_is_applicable_3(self):
        compound = Compound("herbst_anfang")
        self.assertTrue(
            sibilant_fin_is_applicable(compound)
        )

    def test_sibilant_fin_applies_3(self):
        compound = Compound("herbst_anfang")
        self.assertTrue(
            sibilant_fin_applies(compound)
        )

        
    def test_sibilant_fin_is_applicable_4(self):
        compound = Compound("blume_+n_strauß")
        self.assertFalse(
            sibilant_fin_is_applicable(compound)
        )

    def test_sibilant_fin_is_applicable_5(self):
        compound = Compound("kind_+=er_garten")
        self.assertFalse(
            sibilant_fin_is_applicable(compound)
        )



class TestApplicabilityCheckersVowFin(unittest.TestCase):

	# p2l:phon_fin:vow$-0
	#
    # First constituents that are constituted by nouns that end
    # in a full vowel always adopt a zero linker.

    def test_vow_fin_is_applicable_0(self):
        compound = Compound("auto_bahn")
        self.assertTrue(
            vow_fin_is_applicable(compound)
        )

    def test_vow_fin_applies_0(self):
        compound = Compound("auto_bahn")
        self.assertTrue(
            vow_fin_applies(compound)
        )

        
    def test_vow_fin_is_applicable_1(self):
        compound = Compound("uhu_paar")
        self.assertTrue(
            vow_fin_is_applicable(compound)
        )

    def test_vow_fin_applies_1(self):
        compound = Compound("uhu_paar")
        self.assertTrue(
            vow_fin_applies(compound)
        )


    def test_vow_fin_is_applicable_2(self):
        compound = Compound("kuh_milch")
        self.assertTrue(
            vow_fin_is_applicable(compound)
        )

    def test_vow_fin_applies_2(self):
        compound = Compound("kuh_milch")
        self.assertTrue(
            vow_fin_applies(compound)
        )

        
    def test_vow_fin_is_applicable_3(self):
        compound = Compound("gummi_bär")
        self.assertTrue(
            vow_fin_is_applicable(compound)
        )

    def test_vow_fin_applies_3(self):
        compound = Compound("gummi_bär")
        self.assertTrue(
            vow_fin_applies(compound)
        )


    def test_vow_fin_is_applicable_4(self):
        compound = Compound("uhu_+s_nest")
        self.assertTrue(
            vow_fin_is_applicable(compound)
        )

    def test_vow_fin_applies_4(self):
        compound = Compound("uhu_+s_nest")
        self.assertFalse(
            vow_fin_applies(compound)
        )

        
    def test_vow_fin_is_applicable_5(self):
        compound = Compound("blume_+n_topf")
        self.assertFalse(
            vow_fin_is_applicable(compound)
        )

    def test_vow_fin_is_applicable_6(self):
        compound = Compound("reiter_schwert")
        self.assertFalse(
            vow_fin_is_applicable(compound)
        )


    def test_vow_fin_is_applicable_corr_0(self):
        compound = Compound("idee_+n_liste")
        self.assertFalse(
            vow_fin_is_applicable_corr(compound)
        )

    def test_vow_fin_is_applicable_corr_1(self):
        compound = Compound("melodie_+n_folge")
        self.assertFalse(
            vow_fin_is_applicable_corr(compound)
        )



class TestApplicabilityCheckersStressedPhonFin(unittest.TestCase):

	# p2l:phon_fin:F_#stressed_phon$-0
	#
    # First constituents that are constituted by feminine nouns that end 
    # with stressed -ei, -ie, -ur, also stressed or unstressed -ik
    # usually attach a zero linker.

    def test_stressed_phon_fin_is_applicable_0(self):
        compound = Compound("physik_unterricht")
        self.assertTrue(
            stressed_phon_fin_is_applicable(compound)
        )

    def test_stressed_phon_fin_applies_0(self):
        compound = Compound("physik_unterricht")
        self.assertTrue(
            stressed_phon_fin_applies(compound)
        )

    def test_stressed_phon_fin_is_applicable_1(self):
        compound = Compound("akustik_paneele")
        self.assertTrue(
            stressed_phon_fin_is_applicable(compound)
        )

    def test_stressed_phon_fin_applies_1(self):
        compound = Compound("akustik_paneele")
        self.assertTrue(
            stressed_phon_fin_applies(compound)
        )

        
    def test_stressed_phon_fin_is_applicable_2(self):
        compound = Compound("architektur_büro")
        self.assertTrue(
            stressed_phon_fin_is_applicable(compound)
        )

    def test_stressed_phon_fin_applies_2(self):
        compound = Compound("architektur_büro")
        self.assertTrue(
            stressed_phon_fin_applies(compound)
        )

        
    def test_stressed_phon_fin_is_applicable_3(self):
        compound = Compound("metzgerei_produkt")
        self.assertTrue(
            stressed_phon_fin_is_applicable(compound)
        )

    def test_stressed_phon_fin_applies_3(self):
        compound = Compound("metzgerei_produkt")
        self.assertTrue(
            stressed_phon_fin_applies(compound)
        )

        
    def test_stressed_phon_fin_is_applicable_4(self):
        compound = Compound("kultur_+en_folge")
        self.assertTrue(
            stressed_phon_fin_is_applicable(compound)
        )

    def test_stressed_phon_fin_applies_4(self):
        compound = Compound("kultur_+en_folge")
        self.assertFalse(
            stressed_phon_fin_applies(compound)
        )


    def test_stressed_phon_fin_is_applicable_5(self):
        compound = Compound("melodie_+n_reigen")
        self.assertTrue(
            stressed_phon_fin_is_applicable(compound)
        )

    def test_stressed_phon_fin_applies_5(self):
        compound = Compound("melodie_+n_reigen")
        self.assertFalse(
            stressed_phon_fin_applies(compound)
        )

        
    def test_stressed_phon_fin_is_applicable_6(self):
        compound = Compound("bedarf_+s_lage")
        self.assertFalse(
            stressed_phon_fin_is_applicable(compound)
        )

    def test_stressed_phon_fin_is_applicable_7(self):
        compound = Compound("abstieg_+s_angst")
        self.assertFalse(
            stressed_phon_fin_is_applicable(compound)
        )



class TestApplicabilityCheckersFTFin(unittest.TestCase):

	# p2l:phon_fin:F_stem_#t$-s
	#
    # First constituents that are constituted by polysyllabic feminine nouns
    # that end with [t] often attach -s- if the [t] is not part of a suffix
    # -(ig)keit, -heit, -schaft, or -ität or its allomorphs.

    def test_f_t_fin_is_applicable_0(self):
        compound = Compound("arbeit_+s_tag")
        self.assertTrue(
            f_t_fin_is_applicable(compound)
        )

    def test_f_t_fin_applies_0(self):
        compound = Compound("arbeit_+s_tag")
        self.assertTrue(
            f_t_fin_applies(compound)
        )

        
    def test_f_t_fin_is_applicable_1(self):
        compound = Compound("heirat_+s_antrag")
        self.assertTrue(
            f_t_fin_is_applicable(compound)
        )

    def test_f_t_fin_applies_1(self):
        compound = Compound("heirat_+s_antrag")
        self.assertTrue(
            f_t_fin_applies(compound)
        )

        
    def test_f_t_fin_is_applicable_2(self):
        compound = Compound("zukunft_+s_angst")
        self.assertTrue(
            f_t_fin_is_applicable(compound)
        )

    def test_f_t_fin_applies_2(self):
        compound = Compound("zukunft_+s_angst")
        self.assertTrue(
            f_t_fin_applies(compound)
        )

        
    def test_f_t_fin_is_applicable_3(self):
        compound = Compound("arbeit_geber")
        self.assertTrue(
            f_t_fin_is_applicable(compound)
        )

    def test_f_t_fin_applies_3(self):
        compound = Compound("arbeit_geber")
        self.assertFalse(
            f_t_fin_applies(compound)
        )

        
    def test_f_t_fin_is_applicable_4(self):
        compound = Compound("schuld_gefühl")
        self.assertFalse(
            f_t_fin_is_applicable(compound)
        )

    def test_f_t_fin_is_applicable_5(self):
        compound = Compound("sicht_schutz")
        self.assertFalse(
            f_t_fin_is_applicable(compound)
        )
        
    def test_f_t_fin_is_applicable_6(self):
        compound = Compound("tätigkeit_+s_bereich")
        self.assertFalse(
            f_t_fin_is_applicable(compound)
        )

    def test_f_t_fin_is_applicable_7(self):
        compound = Compound("qualität_+s_probe")
        self.assertFalse(
            f_t_fin_is_applicable(compound)
        )



class TestApplicabilityCheckersSchwaFin(unittest.TestCase):

	# p2l:phon_fin:schwa$-en|def-en
	#
	# First constituents that are constituted by nouns
    # that end in schwa mostly adopt -n-.

    def test_schwa_fin_is_applicable_0(self):
        compound = Compound("biene_+n_zucht")
        self.assertTrue(
            schwa_fin_is_applicable(compound)
        )

    def test_schwa_fin_applies_0(self):
        compound = Compound("biene_+n_zucht")
        self.assertTrue(
            schwa_fin_applies(compound)
        )

        
    def test_schwa_fin_is_applicable_1(self):
        compound = Compound("suppe_+n_schüssel")
        self.assertTrue(
            schwa_fin_is_applicable(compound)
        )

    def test_schwa_fin_applies_1(self):
        compound = Compound("suppe_+n_schüssel")
        self.assertTrue(
            schwa_fin_applies(compound)
        )

        
    def test_schwa_fin_is_applicable_2(self):
        compound = Compound("auge_+n_lied")
        self.assertTrue(
            schwa_fin_is_applicable(compound)
        )

    def test_schwa_fin_applies_2(self):
        compound = Compound("auge_+n_lied")
        self.assertTrue(
            schwa_fin_applies(compound)
        )

        
    def test_schwa_fin_is_applicable_3(self):
        compound = Compound("fläche_maß")
        self.assertTrue(
            schwa_fin_is_applicable(compound)
        )

    def test_schwa_fin_applies_3(self):
        compound = Compound("fläche_maß")
        self.assertFalse(
            schwa_fin_applies(compound)
        )

        
    def test_schwa_fin_is_applicable_4(self):
        compound = Compound("sorge_pflicht")
        self.assertTrue(
            schwa_fin_is_applicable(compound)
        )

    def test_schwa_fin_applies_4(self):
        compound = Compound("sorge_pflicht")
        self.assertFalse(
            schwa_fin_applies(compound)
        )

        
    def test_schwa_fin_is_applicable_5(self):
        compound = Compound("gebäude_komplex")
        self.assertTrue(
            schwa_fin_is_applicable(compound)
        )

    def test_schwa_fin_applies_5(self):
        compound = Compound("gebäude_komplex")
        self.assertFalse(
            schwa_fin_applies(compound)
        )

        
    def test_schwa_fin_is_applicable_6(self):
        compound = Compound("idee_+n_liste")
        self.assertFalse(
            schwa_fin_is_applicable(compound)
        )

    def test_schwa_fin_is_applicable_7(self):
        compound = Compound("gummi_bär")
        self.assertFalse(
            schwa_fin_is_applicable(compound)
        )


class TestApplicabilityCheckersSchwaFinF(unittest.TestCase):

	# p2l:phon_fin:schwa$-en|f-en
	#
	# First constituents that are constituted by feminine nouns
    # that end in schwa adopt -n- regularly.

    def test_schwa_fin_f_is_applicable_0(self):
        compound = Compound("biene_+n_zucht")
        self.assertTrue(
            schwa_fin_f_is_applicable(compound)
        )

    def test_schwa_fin_f_applies_0(self):
        compound = Compound("biene_+n_zucht")
        self.assertTrue(
            schwa_fin_f_applies(compound)
        )

        
    def test_schwa_fin_f_is_applicable_1(self):
        compound = Compound("suppe_+n_schüssel")
        self.assertTrue(
            schwa_fin_f_is_applicable(compound)
        )

    def test_schwa_fin_f_applies_1(self):
        compound = Compound("suppe_+n_schüssel")
        self.assertTrue(
            schwa_fin_f_applies(compound)
        )

        
    def test_schwa_fin_is_applicable_2(self):
        compound = Compound("tiefe_+n_meter")
        self.assertTrue(
            schwa_fin_is_applicable(compound)
        )

    def test_schwa_fin_applies_2(self):
        compound = Compound("tiefe_+n_meter")
        self.assertTrue(
            schwa_fin_applies(compound)
        )

        
    def test_schwa_fin_f_is_applicable_3(self):
        compound = Compound("fläche_maß")
        self.assertTrue(
            schwa_fin_f_is_applicable(compound)
        )

    def test_schwa_fin_f_applies_3(self):
        compound = Compound("fläche_maß")
        self.assertFalse(
            schwa_fin_f_applies(compound)
        )

        
    def test_schwa_fin_f_is_applicable_4(self):
        compound = Compound("sorge_pflicht")
        self.assertTrue(
            schwa_fin_f_is_applicable(compound)
        )

    def test_schwa_fin_f_applies_4(self):
        compound = Compound("sorge_pflicht")
        self.assertFalse(
            schwa_fin_f_applies(compound)
        )

        
    def test_schwa_fin_f_is_applicable_5(self):
        compound = Compound("gebäude_komplex")
        self.assertFalse(
            schwa_fin_f_is_applicable(compound)
        )
        
    def test_schwa_fin_f_is_applicable_6(self):
        compound = Compound("idee_+n_liste")
        self.assertFalse(
            schwa_fin_f_is_applicable(compound)
        )

    def test_schwa_fin_f_is_applicable_7(self):
        compound = Compound("gummi_bär")
        self.assertFalse(
            schwa_fin_f_is_applicable(compound)
        )


    # def test_schwa_fin_f_is_applicable_corr_0(self):
    #     compound = Compound("reise_zentrum")
    #     self.assertFalse(
    #         schwa_fin_is_applicable_corr(compound)
    #     )

    # def test_schwa_fin_f_is_applicable_corr_1(self):
    #     compound = Compound("wärme_abgabe")
    #     self.assertFalse(
    #         schwa_fin_is_applicable_corr(compound)
    #     )



class TestApplicabilityCheckersFConsFinSg:

	# p2l:phon_fin:weak_F_cons$-0/s/en|!pl_interpr-0/s
	#
    # First constituents that are constituted by
    # consonant-final weak feminine nouns mostly adopt a zero linker or -s- 
    # in compounds in which the second constituent forces
    # a singular meaning of the given first constituent.

    # def test_f_cons_fin_sg_is_applicable_0(self):
    #     compound = Compound("schrift_führer")
    #     self.assertTrue(
    #         f_cons_fin_sg_is_applicable(compound)
    #     )

    # def test_f_cons_fin_sg_applies_0(self):
    #     compound = Compound("schrift_führer")
    #     self.assertTrue(
    #         f_cons_fin_sg_applies(compound)
    #     )

        
    # def test_f_cons_fin_sg_is_applicable_1(self):
    #     compound = Compound("geburt_+s_tag")
    #     self.assertTrue(
    #         f_cons_fin_sg_is_applicable(compound)
    #     )

    # def test_f_cons_fin_sg_applies_1(self):
    #     compound = Compound("geburt_+s_tag")
    #     self.assertTrue(
    #         f_cons_fin_sg_applies(compound)
    #     )

        
    # def test_f_cons_fin_sg_is_applicable_2(self):
    #     compound = Compound("burg_anlage")
    #     self.assertTrue(
    #         f_cons_fin_sg_is_applicable(compound)
    #     )

    # def test_f_cons_fin_sg_applies_2(self):
    #     compound = Compound("burg_anlage")
    #     self.assertTrue(
    #         f_cons_fin_sg_applies(compound)
    #     )

        
    # def test_f_cons_fin_sg_is_applicable_3(self):
    #     compound = Compound("burg_+en_blick")
    #     self.assertTrue(
    #         f_cons_fin_sg_is_applicable(compound)
    #     )

    # def test_f_cons_fin_sg_applies_3(self):
    #     compound = Compound("burg_+en_blick")
    #     self.assertFalse(
    #         f_cons_fin_sg_applies(compound)
    #     )

        
    # def test_f_cons_fin_sg_is_applicable_4(self):
    #     compound = Compound("frau_+en_bild")
    #     self.assertTrue(
    #         f_cons_fin_sg_is_applicable(compound)
    #     )

    # def test_f_cons_fin_sg_applies_4(self):
    #     compound = Compound("frau_+en_bild")
    #     self.assertFalse(
    #         f_cons_fin_sg_applies(compound)
    #     )

        
    # def test_f_cons_fin_sg_is_applicable_5(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         f_cons_fin_sg_is_applicable(compound)
    #     )

    # def test_f_cons_fin_sg_is_applicable_6(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         f_cons_fin_sg_is_applicable(compound)
    #     )

	pass


class TestApplicabilityCheckersFConsFinPl:

	# p2l:phon_fin:weak_F_cons$-0/s/en|pl_interpr-en
	#
    # First constituents that are constituted by
    # consonant-final weak feminine nouns --- especially final-stressed
    # incl. monosyllabic ones --- attach -en- more likely in compounds
    # in which the second constituent forces
    # a plural meaning of the given first constituent.

    # def test_f_cons_fin_pl_is_applicable_0(self):
    #     compound = Compound("schrift_+en_verzeichnis")
    #     self.assertTrue(
    #         f_cons_fin_pl_is_applicable(compound)
    #     )

    # def test_f_cons_fin_pl_applies_0(self):
    #     compound = Compound("schrift_+en_verzeichnis")
    #     self.assertTrue(
    #         f_cons_fin_pl_applies(compound)
    #     )

        
    # def test_f_cons_fin_pl_is_applicable_1(self):
    #     compound = Compound("geburt_+en_kontrolle")
    #     self.assertTrue(
    #         f_cons_fin_pl_is_applicable(compound)
    #     )

    # def test_f_cons_fin_pl_applies_1(self):
    #     compound = Compound("geburt_+en_kontrolle")
    #     self.assertTrue(
    #         f_cons_fin_pl_applies(compound)
    #     )

        
    # def test_f_cons_fin_pl_is_applicable_2(self):
    #     compound = Compound("burg_+en_land")
    #     self.assertTrue(
    #         f_cons_fin_pl_is_applicable(compound)
    #     )

    # def test_f_cons_fin_pl_applies_2(self):
    #     compound = Compound("burg_+en_land")
    #     self.assertTrue(
    #         f_cons_fin_pl_applies(compound)
    #     )

        
    # def test_f_cons_fin_pl_is_applicable_3(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         f_cons_fin_pl_is_applicable(compound)
    #     )

    # def test_f_cons_fin_pl_is_applicable_4(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         f_cons_fin_pl_is_applicable(compound)
    #     )

	pass



class TestApplicabilityCheckersCopula:

	# p2l:sem:comp_type:copula-0
	#
    # Copulative compounds insert a zero linker regularly.
    # By copulative compounds are understood compounds in which
    # the two constituents do not exhibit a clear modifier-head relation.

    # def test_copula_is_applicable_0(self):
    #     compound = Compound("dichter_componist")
    #     self.assertTrue(
    #         copula_is_applicable(compound)
    #     )

    # def test_copula_applies_0(self):
    #     compound = Compound("dichter_componist")
    #     self.assertTrue(
    #         copula_applies(compound)
    #     )

        
    # def test_copula_is_applicable_1(self):
    #     compound = Compound("bett_sofa")
    #     self.assertTrue(
    #         copula_is_applicable(compound)
    #     )

    # def test_copula_applies_1(self):
    #     compound = Compound("bett_sofa")
    #     self.assertTrue(
    #         copula_applies(compound)
    #     )

        
    # def test_copula_is_applicable_2(self):
    #     compound = Compound("königin_mutter")
    #     self.assertTrue(
    #         copula_is_applicable(compound)
    #     )

    # def test_copula_applies_2(self):
    #     compound = Compound("königin_mutter")
    #     self.assertTrue(
    #         copula_applies(compound)
    #     )

        
    # def test_copula_is_applicable_3(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         copula_is_applicable(compound)
    #     )

    # def test_copula_is_applicable_4(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         copula_is_applicable(compound)
    #     )

	pass



class TestApplicabilityCheckersArgument:

	# p2l:sem:comp_type:arg-s
	#
    # Argumental compounds are sometimes marked by -s-.
    # By argumental compounds are understood compounds in which
    # the second constituent still contains a high degree of verbiness
    # and the first constituent of which constitutes their argument.
    # The second constituent is such compounds is usually
    # an agent designation, an -ung formation etc.

    # def test_argument_is_applicable_0(self):
    #     compound = Compound("gewicht_+s_heber")
    #     self.assertTrue(
    #         argument_is_applicable(compound)
    #     )

    # def test_argument_applies_0(self):
    #     compound = Compound("gewicht_+s_heber")
    #     self.assertTrue(
    #         argument_applies(compound)
    #     )

        
    # def test_argument_is_applicable_1(self):
    #     compound = Compound("krieg_+s_führung")
    #     self.assertTrue(
    #         argument_is_applicable(compound)
    #     )

    # def test_argument_applies_1(self):
    #     compound = Compound("krieg_+s_führung")
    #     self.assertTrue(
    #         argument_applies(compound)
    #     )

        
    # def test_argument_is_applicable_2(self):
    #     compound = Compound("gewicht_heber")
    #     self.assertTrue(
    #         argument_is_applicable(compound)
    #     )

    # def test_argument_applies_2(self):
    #     compound = Compound("gewicht_heber")
    #     self.assertFalse(
    #         argument_applies(compound)
    #     )

        
    # def test_argument_is_applicable_3(self):
    #     compound = Compound("krieg_führung")
    #     self.assertTrue(
    #         argument_is_applicable(compound)
    #     )

    # def test_argument_applies_3(self):
    #     compound = Compound("krieg_führung")
    #     self.assertFalse(
    #         argument_applies(compound)
    #     )

        
    # def test_argument_is_applicable_4(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         argument_is_applicable(compound)
    #     )

    # def test_argument_is_applicable_5(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         argument_is_applicable(compound)
    #     )

	pass



class TestApplicabilityCheckersTechTerm:

	# p2l:sem:tech_term-0
	#
	# Compounds belonging to technical terminology (economics, law,
    # medicine, etc.) are often missing an explicit linking element
    # (even in cases where it would be obligatory in a non-technical context).

    # def test_tech_term_is_applicable_0(self):
    #     compound = Compound("erbschaft_steuer")
    #     self.assertTrue(
    #         tech_term_is_applicable(compound)
    #     )

    # def test_tech_term_applies_0(self):
    #     compound = Compound("erbschaft_steuer")
    #     self.assertTrue(
    #         tech_term_applies(compound)
    #     )

        
    # def test_tech_term_is_applicable_1(self):
    #     compound = Compound("herz_schlagen")
    #     self.assertTrue(
    #         tech_term_is_applicable(compound)
    #     )

    # def test_tech_term_applies_1(self):
    #     compound = Compound("herz_schlagen")
    #     self.assertTrue(
    #         tech_term_applies(compound)
    #     )

        
    # def test_tech_term_is_applicable_2(self):
    #     compound = Compound("schaden_ersatz")
    #     self.assertTrue(
    #         tech_term_is_applicable(compound)
    #     )

    # def test_tech_term_applies_2(self):
    #     compound = Compound("schaden_ersatz")
    #     self.assertTrue(
    #         tech_term_applies(compound)
    #     )

        
    # def test_tech_term_is_applicable_3(self):
    #     compound = Compound("schaden_+s_ersatz")
    #     self.assertTrue(
    #         tech_term_is_applicable(compound)
    #     )

    # def test_tech_term_applies_3(self):
    #     compound = Compound("schaden_+s_ersatz")
    #     self.assertFalse(
    #         tech_term_applies(compound)
    #     )

        
    # def test_tech_term_is_applicable_4(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         tech_term_is_applicable(compound)
    #     )

    # def test_tech_term_is_applicable_5(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         tech_term_is_applicable(compound)
    #     )

	pass



class TestApplicabilityCheckersSecConstAnim:

	# p2l:sem:2const_anim/pers-s
	#
    # Compounds with second constituents 'Mann', 'Frau', 'Leute',
    # 'Tochter', 'Gattin', 'Witwe' tend to insert -s-
    # if the compound designates a person
    # (even if the first constituent would otherwise attach a zero linker).

    # def test_sec_const_anim_is_applicable_0(self):
    #     compound = Compound("reiter_+s_mann")
    #     self.assertTrue(
    #         sec_const_anim_is_applicable(compound)
    #     )

    # def test_sec_const_anim_applies_0(self):
    #     compound = Compound("reiter_+s_mann")
    #     self.assertTrue(
    #         sec_const_anim_applies(compound)
    #     )

        
    # def test_sec_const_anim_is_applicable_1(self):
    #     compound = Compound("lehrer_+s_tochter")
    #     self.assertTrue(
    #         sec_const_anim_is_applicable(compound)
    #     )

    # def test_sec_const_anim_applies_1(self):
    #     compound = Compound("lehrer_+s_tochter")
    #     self.assertTrue(
    #         sec_const_anim_applies(compound)
    #     )

        
    # def test_sec_const_anim_is_applicable_2(self):
    #     compound = Compound("bäcker_+s_leute")
    #     self.assertTrue(
    #         sec_const_anim_is_applicable(compound)
    #     )

    # def test_sec_const_anim_applies_2(self):
    #     compound = Compound("bäcker_+s_leute")
    #     self.assertTrue(
    #         sec_const_anim_applies(compound)
    #     )

        
    # def test_sec_const_anim_is_applicable_3(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         sec_const_anim_is_applicable(compound)
    #     )

    # def test_sec_const_anim_is_applicable_4(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         sec_const_anim_is_applicable(compound)
    #     )

	pass



class TestApplicabilityCheckersCmpxMorph(unittest.TestCase):

	# p2l:tend:cmpx_morph-s|def-s
	#
    # The probability of -s- grows irregularly with the
    # morphological complexity of the first constituent
    # (any form of derivation).

    def test_cmpx_morph_is_applicable_0(self):
        compound = Compound("gesundheit_+s_amt")
        self.assertTrue(
            cmpx_morph_is_applicable(compound)
        )

    def test_cmpx_morph_applies_0(self):
        compound = Compound("gesundheit_+s_amt")
        self.assertTrue(
            cmpx_morph_applies(compound)
        )

        
    def test_cmpx_morph_is_applicable_1(self):
        compound = Compound("gesellschaft_+s_politik")
        self.assertTrue(
            cmpx_morph_is_applicable(compound)
        )

    def test_cmpx_morph_applies_1(self):
        compound = Compound("gesellschaft_+s_politik")
        self.assertTrue(
            cmpx_morph_applies(compound)
        )

        
    def test_cmpx_morph_is_applicable_2(self):
        compound = Compound("anspruch_+s_haltung")
        self.assertTrue(
            cmpx_morph_is_applicable(compound)
        )

    def test_cmpx_morph_applies_2(self):
        compound = Compound("anspruch_+s_haltung")
        self.assertTrue(
            cmpx_morph_applies(compound)
        )

        
    def test_cmpx_morph_is_applicable_3(self):
        compound = Compound("eintrag_+s_frist")
        self.assertTrue(
            cmpx_morph_is_applicable(compound)
        )

    def test_cmpx_morph_applies_3(self):
        compound = Compound("eintrag_+s_frist")
        self.assertTrue(
            cmpx_morph_applies(compound)
        )


    def test_cmpx_morph_is_applicable_4(self):
        compound = Compound("ort_+s_amt")
        self.assertTrue(
            cmpx_morph_is_applicable(compound)
        )

    def test_cmpx_morph_applies_4(self):
        compound = Compound("ort_+s_amt")
        self.assertFalse(
            cmpx_morph_applies(compound)
        )


    def test_cmpx_morph_is_applicable_5(self):
        compound = Compound("krieg_+s_ende")
        self.assertTrue(
            cmpx_morph_is_applicable(compound)
        )

    def test_cmpx_morph_applies_5(self):
        compound = Compound("krieg_+s_ende")
        self.assertFalse(
            cmpx_morph_applies(compound)
        )

        
    def test_cmpx_morph_is_applicable_6(self):
        compound = Compound("minderheit_+en_recht")
        self.assertTrue(
            cmpx_morph_is_applicable(compound)
        )

    def test_cmpx_morph_applies_6(self):
        compound = Compound("minderheit_+en_recht")
        self.assertFalse(
            cmpx_morph_applies(compound)
        )

        
    def test_cmpx_morph_is_applicable_7(self):
        compound = Compound("anruf_beantworter")
        self.assertTrue(
            cmpx_morph_is_applicable(compound)
        )

    def test_cmpx_morph_applies_7(self):
        compound = Compound("anruf_beantworter")
        self.assertFalse(
            cmpx_morph_applies(compound)
        )



class TestApplicabilityCheckersCmpxPhon(unittest.TestCase):

	# p2l:tend:cmpx_phon-s|def-s
	#
    # The probability of -s- grows irregularly with the
    # phonological complexity of the first constituent.
    # By phonologically complex words are understood
    # words with polysyllable non-trochaic form,
    # words with unstressed prefixes,
    # words with stressed or semi-stressed suffixes etc.

    def test_cmpx_phon_is_applicable_0(self):
        compound = Compound("anruf_beantworter")
        self.assertTrue(
            cmpx_phon_is_applicable(compound)
        )

    def test_cmpx_phon_applies_0(self):
        compound = Compound("anruf_beantworter")
        self.assertTrue(
            cmpx_phon_applies(compound)
        )

        
    def test_cmpx_phon_is_applicable_1(self):
        compound = Compound("beruf_+s_erfahrung")
        self.assertTrue(
            cmpx_phon_is_applicable(compound)
        )

    def test_cmpx_phon_applies_1(self):
        compound = Compound("beruf_+s_erfahrung")
        self.assertTrue(
            cmpx_phon_applies(compound)
        )

        
    def test_cmpx_phon_is_applicable_2(self):
        compound = Compound("religion_+s_unterricht")
        self.assertTrue(
            cmpx_phon_is_applicable(compound)
        )

    def test_cmpx_phon_applies_2(self):
        compound = Compound("religion_+s_unterricht")
        self.assertTrue(
            cmpx_phon_applies(compound)
        )

        
    def test_cmpx_phon_is_applicable_3(self):
        compound = Compound("schlaf_plan")
        self.assertTrue(
            cmpx_phon_is_applicable(compound)
        )

    def test_cmpx_phon_applies_3(self):
        compound = Compound("schlaf_plan")
        self.assertTrue(
            cmpx_phon_applies(compound)
        )

        
    def test_cmpx_phon_is_applicable_4(self):
        compound = Compound("rarität_+en_laden")
        self.assertTrue(
            cmpx_phon_is_applicable(compound)
        )

    def test_cmpx_phon_applies_4(self):
        compound = Compound("rarität_+en_laden")
        self.assertFalse(
            cmpx_phon_applies(compound)
        )

        
    def test_cmpx_phon_is_applicable_5(self):
        compound = Compound("bestand_teil")
        self.assertTrue(
            cmpx_phon_is_applicable(compound)
        )

    def test_cmpx_phon_applies_5(self):
        compound = Compound("bestand_teil")
        self.assertFalse(
            cmpx_phon_applies(compound)
        )



class TestApplicabilityCheckersSonority(unittest.TestCase):

	# p2l:tend:sonority-!s
	#
    # The probability of -s- in compounds with simplex first constituents
    # tends to decrease with the increasing sonority of the final segment
    # of the first constituent. -s- is thus more frequent after plosives,
    # infrequent after nasals and liquids,
    # and it never occurs after a full vowel.

    def test_sonority_is_applicable_0(self):
        compound = Compound("ort_+s_tarif")
        self.assertTrue(
            sonority_is_applicable(compound)
        )

    def test_sonority_applies_0(self):
        compound = Compound("ort_+s_tarif")
        self.assertTrue(
            sonority_applies(compound)
        )

        
    def test_sonority_is_applicable_1(self):
        compound = Compound("glück_+s_rad")
        self.assertTrue(
            sonority_is_applicable(compound)
        )

    def test_sonority_applies_1(self):
        compound = Compound("glück_+s_rad")
        self.assertTrue(
            sonority_applies(compound)
        )

        
    def test_sonority_is_applicable_2(self):
        compound = Compound("himmel_reich")
        self.assertTrue(
            sonority_is_applicable(compound)
        )

    def test_sonority_applies_2(self):
        compound = Compound("himmel_reich")
        self.assertTrue(
            sonority_applies(compound)
        )

        
    def test_sonority_is_applicable_3(self):
        compound = Compound("uhu_paar")
        self.assertTrue(
            sonority_is_applicable(compound)
        )

    def test_sonority_applies_3(self):
        compound = Compound("uhu_paar")
        self.assertTrue(
            sonority_applies(compound)
        )

        
    def test_sonority_is_applicable_4(self):
        compound = Compound("arbeit_geber")
        self.assertTrue(
            sonority_is_applicable(compound)
        )

    def test_sonority_applies_4(self):
        compound = Compound("arbeit_geber")
        self.assertFalse(
            sonority_applies(compound)
        )


    def test_sonority_is_applicable_5(self):
        compound = Compound("dieb_stahl")
        self.assertTrue(
            sonority_is_applicable(compound)
        )

    def test_sonority_applies_5(self):
        compound = Compound("dieb_stahl")
        self.assertFalse(
            sonority_applies(compound)
        )

        
    def test_sonority_is_applicable_6(self):
        compound = Compound("himmel_+s_bahn")
        self.assertTrue(
            sonority_is_applicable(compound)
        )

    def test_sonority_applies_6(self):
        compound = Compound("himmel_+s_bahn")
        self.assertFalse(
            sonority_applies(compound)
        )

        
    def test_sonority_is_applicable_7(self):
        compound = Compound("uhu_+s_nest")
        self.assertTrue(
            sonority_is_applicable(compound)
        )

    def test_sonority_applies_7(self):
        compound = Compound("uhu_+s_nest")
        self.assertFalse(
            sonority_applies(compound)
        )

    # none of the sources explicitly
	# mention the effect of the constraint 
    # on the occurrence of -s- after fricatives
    def test_sonority_is_applicable_8(self):
        compound = Compound("gefäß_system")
        self.assertFalse(
            sonority_is_applicable(compound)
        )

    def test_sonority_is_applicable_9(self):
        compound = Compound("abstieg_+s_angst")
        self.assertFalse(
            sonority_is_applicable(compound)
        )



class TestApplicabilityCheckersSSmpx(unittest.TestCase):

	# l2p:s|smpx_mn
	#
    # All except for a few simplex nouns that constitute first constituents
    # that attach -s- belong to a small fixed group
    # of masculine and neuter nouns.

    def test_s_smpx_is_applicable_0(self):
        compound = Compound("amt_+s_leiter")
        self.assertTrue(
            s_smpx_is_applicable(compound)
        )

    def test_s_smpx_applies_0(self):
        compound = Compound("amt_+s_leiter")
        self.assertTrue(
            s_smpx_applies(compound)
        )

        
    def test_s_smpx_is_applicable_1(self):
        compound = Compound("ort_+s_angabe")
        self.assertTrue(
            s_smpx_is_applicable(compound)
        )

    def test_s_smpx_applies_1(self):
        compound = Compound("ort_+s_angabe")
        self.assertTrue(
            s_smpx_applies(compound)
        )

        
    def test_s_smpx_is_applicable_2(self):
        compound = Compound("könig_+s_haus")
        self.assertTrue(
            s_smpx_is_applicable(compound)
        )

    def test_s_smpx_applies_2(self):
        compound = Compound("könig_+s_haus")
        self.assertTrue(
            s_smpx_applies(compound)
        )

        
    def test_s_smpx_is_applicable_3(self):
        compound = Compound("arbeit_+s_amt")
        self.assertTrue(
            s_smpx_is_applicable(compound)
        )

    def test_s_smpx_applies_3(self):
        compound = Compound("arbeit_+s_amt")
        self.assertFalse(
            s_smpx_applies(compound)
        )

        
    def test_s_smpx_is_applicable_4(self):
        compound = Compound("heirat_+s_antrag")
        self.assertTrue(
            s_smpx_is_applicable(compound)
        )

    def test_s_smpx_applies_4(self):
        compound = Compound("heirat_+s_antrag")
        self.assertFalse(
            s_smpx_applies(compound)
        )

        
    # def test_s_smpx_is_applicable_5(self):
    #     compound = Compound("liebe_+s_brief") 'Liebe' is deadj in CELEX
    #     self.assertTrue(
    #         s_smpx_is_applicable(compound)
    #     )

    # def test_s_smpx_applies_5(self):
    #     compound = Compound("liebe_+s_brief")
    #     self.assertFalse(
    #         s_smpx_applies(compound)
    #     )

        
    def test_s_smpx_is_applicable_6(self):
        compound = Compound("beruf_+s_erfahrung")
        self.assertFalse(
            s_smpx_is_applicable(compound)
        )

    def test_s_smpx_is_applicable_7(self):
        compound = Compound("wohnung_+s_geber")
        self.assertFalse(
            s_smpx_is_applicable(compound)
        )


class TestApplicabilityCheckersSFreq(unittest.TestCase):

	# l2p:s|smpx_high_freq
	#
    # Many simplex nouns that constitute first constituents
    # that attach -s- have a high token frequency.

    def test_s_freq_is_applicable_0(self):
        compound = Compound("volk_+s_brauch")
        self.assertTrue(
            s_freq_is_applicable(compound)
        )

    def test_s_freq_applies_0(self):
        compound = Compound("volk_+s_brauch")
        self.assertTrue(
            s_freq_applies(compound)
        )

        
    def test_s_freq_is_applicable_1(self):
        compound = Compound("amt_+s_anwalt")
        self.assertTrue(
            s_freq_is_applicable(compound)
        )

    def test_s_freq_applies_1(self):
        compound = Compound("amt_+s_anwalt")
        self.assertTrue(
            s_freq_applies(compound)
        )

        
    def test_s_freq_is_applicable_2(self):
        compound = Compound("staat_+s_amt")
        self.assertTrue(
            s_freq_is_applicable(compound)
        )

    def test_s_freq_applies_2(self):
        compound = Compound("staat_+s_amt")
        self.assertTrue(
            s_freq_applies(compound)
        )

        
    def test_s_freq_is_applicable_3(self):
        compound = Compound("beruf_+s_erfahrung")
        self.assertFalse(
            s_freq_is_applicable(compound)
        )

    def test_s_freq_is_applicable_4(self):
        compound = Compound("wohnung_+s_geber")
        self.assertFalse(
            s_freq_is_applicable(compound)
        )


class TestApplicabilityCheckersSFCmpx(unittest.TestCase):

	# l2p:s|f_cmpx
	#
    # Almost all feminine nouns that constitute first constituents
    # that attach -s- are morphologically complex.

    def test_s_f_cmpx_is_applicable_0(self):
        compound = Compound("gesundheit_+s_amt")
        self.assertTrue(
            s_f_cmpx_is_applicable(compound)
        )

    def test_s_f_cmpx_applies_0(self):
        compound = Compound("gesundheit_+s_amt")
        self.assertTrue(
            s_f_cmpx_applies(compound)
        )

        
    def test_s_f_cmpx_is_applicable_1(self):
        compound = Compound("gesellschaft_+s_politik")
        self.assertTrue(
            s_f_cmpx_is_applicable(compound)
        )

    def test_s_f_cmpx_applies_1(self):
        compound = Compound("gesellschaft_+s_politik")
        self.assertTrue(
            s_f_cmpx_applies(compound)
        )

        
    def test_s_f_cmpx_is_applicable_2(self):
        compound = Compound("liebe_+s_brief")
        self.assertTrue(
            s_f_cmpx_is_applicable(compound)
        )

    def test_s_f_cmpx_applies_2(self):
        compound = Compound("liebe_+s_brief")
        self.assertTrue(
            s_f_cmpx_applies(compound)
        )


    def test_s_f_cmpx_is_applicable_3(self):
        compound = Compound("arbeit_+s_tag")
        self.assertTrue(
            s_f_cmpx_is_applicable(compound)
        )

    def test_s_f_cmpx_applies_3(self):
        compound = Compound("arbeit_+s_tag")
        self.assertFalse(
            s_f_cmpx_applies(compound)
        )


    def test_s_f_cmpx_is_applicable_4(self):
        compound = Compound("heirat_+s_antrag")
        self.assertTrue(
            s_f_cmpx_is_applicable(compound)
        )

    def test_s_f_cmpx_applies_4(self):
        compound = Compound("heirat_+s_antrag")
        self.assertFalse(
            s_f_cmpx_applies(compound)
        )

        
    def test_s_f_cmpx_is_applicable_5(self):
        compound = Compound("ort_+s_amt")
        self.assertFalse(
            s_f_cmpx_is_applicable(compound)
        )

    def test_s_f_cmpx_is_applicable_6(self):
        compound = Compound("alter_+s_abstand")
        self.assertFalse(
            s_f_cmpx_is_applicable(compound)
        )


class TestApplicabilityCheckersSFPolysyl(unittest.TestCase):

	# l2p:s|f_poly_syl
	#
    # Almost all feminine nouns that constitute first constituents
    # that attach -s- are polysyllabic.

    def test_s_f_polysyl_is_applicable_0(self):
        compound = Compound("gesundheit_+s_amt")
        self.assertTrue(
            s_f_polysyl_is_applicable(compound)
        )

    def test_s_f_polysyl_applies_0(self):
        compound = Compound("gesundheit_+s_amt")
        self.assertTrue(
            s_f_polysyl_applies(compound)
        )

        
    def test_s_f_polysyl_is_applicable_1(self):
        compound = Compound("gesellschaft_+s_politik")
        self.assertTrue(
            s_f_polysyl_is_applicable(compound)
        )

    def test_s_f_polysyl_applies_1(self):
        compound = Compound("gesellschaft_+s_politik")
        self.assertTrue(
            s_f_polysyl_applies(compound)
        )

        
    def test_s_f_polysyl_is_applicable_2(self):
        compound = Compound("liebe_+s_brief")
        self.assertTrue(
            s_f_polysyl_is_applicable(compound)
        )

    def test_s_f_polysyl_applies_2(self):
        compound = Compound("liebe_+s_brief")
        self.assertTrue(
            s_f_polysyl_applies(compound)
        )


    def test_s_f_polysyl_is_applicable_3(self):
        compound = Compound("arbeit_+s_tag")
        self.assertTrue(
            s_f_polysyl_is_applicable(compound)
        )

    def test_s_f_polysyl_applies_3(self):
        compound = Compound("arbeit_+s_tag")
        self.assertTrue(
            s_f_polysyl_applies(compound)
        )


    def test_s_f_polysyl_is_applicable_4(self):
        compound = Compound("heirat_+s_antrag")
        self.assertTrue(
            s_f_polysyl_is_applicable(compound)
        )

    def test_s_f_polysyl_applies_4(self):
        compound = Compound("heirat_+s_antrag")
        self.assertTrue(
            s_f_polysyl_applies(compound)
        )

        
    def test_s_f_polysyl_is_applicable_5(self):
        compound = Compound("ort_+s_amt")
        self.assertFalse(
            s_f_polysyl_is_applicable(compound)
        )

    def test_s_f_polysyl_is_applicable_6(self):
        compound = Compound("alter_+s_abstand")
        self.assertFalse(
            s_f_polysyl_is_applicable(compound)
        )



class TestApplicabilityCheckersNSchwa(unittest.TestCase):

	# l2p:n
	#
    # All nouns that constitute first constituents
    # that attach the -n- allomorph of the -en- linker end in schwa.

    def test_n_schwa_is_applicable_0(self):
        compound = Compound("biene_+n_zucht")
        self.assertTrue(
            n_schwa_is_applicable(compound)
        )

    def test_n_schwa_applies_0(self):
        compound = Compound("biene_+n_zucht")
        self.assertTrue(
            n_schwa_applies(compound)
        )

        
    def test_n_schwa_is_applicable_1(self):
        compound = Compound("suppe_+n_schüssel")
        self.assertTrue(
            n_schwa_is_applicable(compound)
        )

    def test_n_schwa_applies_1(self):
        compound = Compound("suppe_+n_schüssel")
        self.assertTrue(
            n_schwa_applies(compound)
        )

        
    def test_n_schwa_is_applicable_2(self):
        compound = Compound("auge_+n_lied")
        self.assertTrue(
            n_schwa_is_applicable(compound)
        )

    def test_n_schwa_applies_2(self):
        compound = Compound("auge_+n_lied")
        self.assertTrue(
            n_schwa_applies(compound)
        )

        
    def test_n_schwa_is_applicable_3(self):
        compound = Compound("kind_+er_garten")
        self.assertFalse(
            n_schwa_is_applicable(compound)
        )

    def test_n_schwa_is_applicable_4(self):
        compound = Compound("burg_+en_land")
        self.assertFalse(
            n_schwa_is_applicable(compound)
        )

    def test_n_schwa_is_applicable_5(self):
        compound = Compound("melodie_+n_folge")
        self.assertFalse(
            n_schwa_is_applicable(compound)
        )

    def test_n_schwa_is_applicable_6(self):
        compound = Compound("kategorie_+n_liste")
        self.assertFalse(
            n_schwa_is_applicable(compound)
        )

    def test_n_schwa_is_applicable_7(self):
        compound = Compound("idee_+n_austausch")
        self.assertFalse(
            n_schwa_is_applicable(compound)
        )


    def test_n_schwa_is_applicable_corr_0(self):
        compound = Compound("oper_+n_haus")
        self.assertTrue(
            n_schwa_is_applicable_corr(compound)
        )

    def test_n_schwa_applies_corr_0(self):
        compound = Compound("oper_+n_haus")
        self.assertTrue(
            n_schwa_applies_corr(compound)
        )

    
    def test_n_schwa_is_applicable_corr_1(self):
        compound = Compound("schwester_+n_verbund")
        self.assertTrue(
            n_schwa_is_applicable_corr(compound)
        )

    def test_n_schwa_applies_corr_1(self):
        compound = Compound("schwester_+n_verbund")
        self.assertTrue(
            n_schwa_applies_corr(compound)
        )



class TestApplicabilityCheckersEnPar(unittest.TestCase):

	# l2p:en|par
	#
    # All nouns that constitute first constituents
    # that attach -(e)n- belong are weak nouns.

    def test_en_par_is_applicable_0(self):
        compound = Compound("blume_+n_topf")
        self.assertTrue(
            en_par_is_applicable(compound)
        )

    def test_en_par_applies_0(self):
        compound = Compound("blume_+n_topf")
        self.assertTrue(
            en_par_applies(compound)
        )

        
    def test_en_par_is_applicable_1(self):
        compound = Compound("katze_+n_fell")
        self.assertTrue(
            en_par_is_applicable(compound)
        )

    def test_en_par_applies_1(self):
        compound = Compound("katze_+n_fell")
        self.assertTrue(
            en_par_applies(compound)
        )

        
    def test_en_par_is_applicable_2(self):
        compound = Compound("frau_+en_hand")
        self.assertTrue(
            en_par_is_applicable(compound)
        )

    def test_en_par_applies_2(self):
        compound = Compound("frau_+en_hand")
        self.assertTrue(
            en_par_applies(compound)
        )

        
    def test_en_par_is_applicable_3(self):
        compound = Compound("hahn_+en_kamm")
        self.assertTrue(
            en_par_is_applicable(compound)
        )

    def test_en_par_applies_3(self):
        compound = Compound("hahn_+en_kamm")
        self.assertFalse(
            en_par_applies(compound)
        )

        
    def test_en_par_is_applicable_4(self):
        compound = Compound("mond_+en_schein")
        self.assertTrue(
            en_par_is_applicable(compound)
        )

    def test_en_par_applies_4(self):
        compound = Compound("mond_+en_schein")
        self.assertFalse(
            en_par_applies(compound)
        )

        
    def test_en_par_is_applicable_5(self):
        compound = Compound("instrument_+en_bau")
        self.assertTrue(
            en_par_is_applicable(compound)
        )

    def test_en_par_applies_5(self):
        compound = Compound("instrument_+en_bau")
        self.assertFalse(
            en_par_applies(compound)
        )

        
    def test_en_par_is_applicable_6(self):
        compound = Compound("haus_tür")
        self.assertFalse(
            en_par_is_applicable(compound)
        )

    def test_en_par_is_applicable_7(self):
        compound = Compound("hund_+e_leine")
        self.assertFalse(
            en_par_is_applicable(compound)
        )


class TestApplicabilityCheckersEnNonParM:

	# l2p:en|non_par_m
	#
    # All masculine nouns that do not build the plural form with -(e)n
    # that constitute first constituents that attach -(e)n-
    # are monosyllabic designations of male persons, animals,
    # astronomic objects, months.

    # def test_en_non_par_m_is_applicable_0(self):
    #     compound = Compound("hahn_+en_kamm")
    #     self.assertTrue(
    #         en_non_par_m_is_applicable(compound)
    #     )

    # def test_en_non_par_m_applies_0(self):
    #     compound = Compound("hahn_+en_kamm")
    #     self.assertTrue(
    #         en_non_par_m_applies(compound)
    #     )

        
    # def test_en_non_par_m_is_applicable_1(self):
    #     compound = Compound("mond_+en_schein")
    #     self.assertTrue(
    #         en_non_par_m_is_applicable(compound)
    #     )

    # def test_en_non_par_m_applies_1(self):
    #     compound = Compound("mond_+en_schein")
    #     self.assertTrue(
    #         en_non_par_m_applies(compound)
    #     )

        
    # def test_en_non_par_m_is_applicable_2(self):
    #     compound = Compound("stern_+en_himmel")
    #     self.assertTrue(
    #         en_non_par_m_is_applicable(compound)
    #     )

    # def test_en_non_par_m_applies_2(self):
    #     compound = Compound("stern_+en_himmel")
    #     self.assertTrue(
    #         en_non_par_m_applies(compound)
    #     )

        
    # def test_en_non_par_m_is_applicable_3(self):
    #     compound = Compound("mai_+en_nacht")
    #     self.assertTrue(
    #         en_non_par_m_is_applicable(compound)
    #     )

    # def test_en_non_par_m_applies_3(self):
    #     compound = Compound("mai_+en_nacht")
    #     self.assertTrue(
    #         en_non_par_m_applies(compound)
    #     )

        
    # def test_en_non_par_m_is_applicable_4(self):
    #     compound = Compound("mond_aufgang")
    #     self.assertTrue(
    #         en_non_par_m_is_applicable(compound)
    #     )

    # def test_en_non_par_m_applies_4(self):
    #     compound = Compound("mond_aufgang")
    #     self.assertFalse(
    #         en_non_par_m_applies(compound)
    #     )

        
    # def test_en_non_par_m_is_applicable_5(self):
    #     compound = Compound("stern_bild")
    #     self.assertTrue(
    #         en_non_par_m_is_applicable(compound)
    #     )

    # def test_en_non_par_m_applies_5(self):
    #     compound = Compound("stern_bild")
    #     self.assertFalse(
    #         en_non_par_m_applies(compound)
    #     )

        
    # def test_en_non_par_m_is_applicable_6(self):
    #     compound = Compound("mai_baum")
    #     self.assertTrue(
    #         en_non_par_m_is_applicable(compound)
    #     )

    # def test_en_non_par_m_applies_6(self):
    #     compound = Compound("mai_baum")
    #     self.assertFalse(
    #         en_non_par_m_applies(compound)
    #     )

        
    # def test_en_non_par_m_is_applicable_7(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         en_non_par_m_is_applicable(compound)
    #     )

    # def test_en_non_par_m_is_applicable_8(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         en_non_par_m_is_applicable(compound)
    #     )

	pass


class TestApplicabilityCheckersEnNonParNPl:

	# l2p:en|non_par_n_pl_interpr
	#
    # All neuter nouns that do not build the plural form with -(e)n
    # that constitute first constituents that attach -(e)n-
    # are polysyllabic foreign nouns that have a stressed final syllable
    # (and mostly end in -at and -ment) that exhibit
    # a plural meaning within the compound.

    # def test_en_non_par_n_pl_is_applicable_0(self):
    #     compound = Compound("instrument_+en_bau")
    #     self.assertTrue(
    #         en_non_par_n_pl_is_applicable(compound)
    #     )

    # def test_en_non_par_n_pl_applies_0(self):
    #     compound = Compound("instrument_+en_bau")
    #     self.assertTrue(
    #         en_non_par_n_pl_applies(compound)
    #     )

        
    # def test_en_non_par_n_pl_is_applicable_1(self):
    #     compound = Compound("dokument_+en_sammlung")
    #     self.assertTrue(
    #         en_non_par_n_pl_is_applicable(compound)
    #     )

    # def test_en_non_par_n_pl_applies_1(self):
    #     compound = Compound("dokument_+en_sammlung")
    #     self.assertTrue(
    #         en_non_par_n_pl_applies(compound)
    #     )

        
    # def test_en_non_par_n_pl_is_applicable_2(self):
    #     compound = Compound("zertifikat_system")
    #     self.assertTrue(
    #         en_non_par_n_pl_is_applicable(compound)
    #     )

    # def test_en_non_par_n_pl_applies_2(self):
    #     compound = Compound("zertifikat_system")
    #     self.assertFalse(
    #         en_non_par_n_pl_applies(compound)
    #     )

        
    # def test_en_non_par_n_pl_is_applicable_3(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         en_non_par_n_pl_is_applicable(compound)
    #     )

    # def test_en_non_par_n_pl_is_applicable_4(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         en_non_par_n_pl_is_applicable(compound)
    #     )

	pass



class TestApplicabilityCheckersEPar(unittest.TestCase):

	# l2p:e|par
	#
    # All nouns that constitute first constituents that attach -e-
    # build the plural form with -e.

    def test_e_par_is_applicable_0(self):
        compound = Compound("tag_+e_buch")
        self.assertTrue(
            e_par_is_applicable(compound)
        )

    def test_e_par_applies_0(self):
        compound = Compound("tag_+e_buch")
        self.assertTrue(
            e_par_applies(compound)
        )

        
    def test_e_par_is_applicable_1(self):
        compound = Compound("punkt_+e_stand")
        self.assertTrue(
            e_par_is_applicable(compound)
        )

    def test_e_par_applies_1(self):
        compound = Compound("punkt_+e_stand")
        self.assertTrue(
            e_par_applies(compound)
        )

        
    def test_e_par_is_applicable_2(self):
        compound = Compound("hund_+e_leine")
        self.assertTrue(
            e_par_is_applicable(compound)
        )

    def test_e_par_applies_2(self):
        compound = Compound("hund_+e_leine")
        self.assertTrue(
            e_par_applies(compound)
        )

        
    def test_e_par_is_applicable_3(self):
        compound = Compound("herz_+e_leid")
        self.assertTrue(
            e_par_is_applicable(compound)
        )

    def test_e_par_applies_3(self):
        compound = Compound("herz_+e_leid")
        self.assertFalse(
            e_par_applies(compound)
        )

        
    def test_e_par_is_applicable_4(self):
        compound = Compound("haus_tür")
        self.assertFalse(
            e_par_is_applicable(compound)
        )

    def test_e_par_is_applicable_5(self):
        compound = Compound("dokument_+en_sammlung")
        self.assertFalse(
            e_par_is_applicable(compound)
        )


class TestApplicabilityCheckersELastSyl(unittest.TestCase):

	# l2p:e|#stressed_syl
	#
    # All nouns that constitute first constituents that attach -e-
    # have a stressed last syllable.

    def test_e_last_syl_is_applicable_0(self):
        compound = Compound("tag_+e_buch")
        self.assertTrue(
            e_last_syl_is_applicable(compound)
        )

    def test_e_last_syl_applies_0(self):
        compound = Compound("tag_+e_buch")
        self.assertTrue(
            e_last_syl_applies(compound)
        )

        
    def test_e_last_syl_is_applicable_1(self):
        compound = Compound("punkt_+e_stand")
        self.assertTrue(
            e_last_syl_is_applicable(compound)
        )

    def test_e_last_syl_applies_1(self):
        compound = Compound("punkt_+e_stand")
        self.assertTrue(
            e_last_syl_applies(compound)
        )

        
    def test_e_last_syl_is_applicable_2(self):
        compound = Compound("hund_+e_leine")
        self.assertTrue(
            e_last_syl_is_applicable(compound)
        )

    def test_e_last_syl_applies_2(self):
        compound = Compound("hund_+e_leine")
        self.assertTrue(
            e_last_syl_applies(compound)
        )

        
    def test_e_last_syl_is_applicable_3(self):
        compound = Compound("anhalt_+e_stelle")
        self.assertTrue(
            e_last_syl_is_applicable(compound)
        )

    def test_e_last_syl_applies_3(self):
        compound = Compound("anhalt_+e_stelle")
        self.assertFalse(
            e_last_syl_applies(compound)
        )

        
    def test_e_last_syl_is_applicable_4(self):
        compound = Compound("haus_tür")
        self.assertFalse(
            e_last_syl_is_applicable(compound)
        )

    def test_e_last_syl_is_applicable_5(self):
        compound = Compound("dokument_+en_sammlung")
        self.assertFalse(
            e_last_syl_is_applicable(compound)
        )


    def test_e_last_syl_is_applicable_corr_0(self):
        compound = Compound("anhalt_+e_stelle")
        self.assertTrue(
            e_last_syl_is_applicable_corr(compound)
        )

    def test_e_last_syl_applies_corr_0(self):
        compound = Compound("anhalt_+e_stelle")
        self.assertTrue(
            e_last_syl_applies_corr(compound)
        )


class TestApplicabilityCheckersESmpx(unittest.TestCase):

	# l2p:e|smpx
	#
    # Most nouns that constitute first constituents that attach -e- are simplex.

    def test_e_smpx_is_applicable_0(self):
        compound = Compound("tag_+e_buch")
        self.assertTrue(
            e_smpx_is_applicable(compound)
        )

    def test_e_smpx_applies_0(self):
        compound = Compound("tag_+e_buch")
        self.assertTrue(
            e_smpx_applies(compound)
        )

        
    def test_e_smpx_is_applicable_1(self):
        compound = Compound("punkt_+e_stand")
        self.assertTrue(
            e_smpx_is_applicable(compound)
        )

    def test_e_smpx_applies_1(self):
        compound = Compound("punkt_+e_stand")
        self.assertTrue(
            e_smpx_applies(compound)
        )

        
    def test_e_smpx_is_applicable_2(self):
        compound = Compound("hund_+e_leine")
        self.assertTrue(
            e_smpx_is_applicable(compound)
        )

    def test_e_smpx_applies_2(self):
        compound = Compound("hund_+e_leine")
        self.assertTrue(
            e_smpx_applies(compound)
        )

        
    def test_e_smpx_is_applicable_3(self):
        compound = Compound("anhalt_+e_stelle")
        self.assertTrue(
            e_smpx_is_applicable(compound)
        )

    def test_e_smpx_applies_3(self):
        compound = Compound("anhalt_+e_stelle")
        self.assertFalse(
            e_smpx_applies(compound)
        )

        
    def test_e_smpx_is_applicable_4(self):
        compound = Compound("haus_tür")
        self.assertFalse(
            e_smpx_is_applicable(compound)
        )

    def test_e_smpx_is_applicable_5(self):
        compound = Compound("dokument_+en_sammlung")
        self.assertFalse(
            e_smpx_is_applicable(compound)
        )


class TestApplicabilityCheckersENonLoan(unittest.TestCase):

	# l2p:e|!loan
	#
    # All nouns that constitute first constituents that attach -e-
    # are native (none are loanwords).

    # def test_e_non_loan_is_applicable_0(self):
    #     compound = Compound("tag_+e_buch")
    #     self.assertTrue(
    #         e_non_loan_is_applicable(compound)
    #     )

    # def test_e_non_loan_applies_0(self):
    #     compound = Compound("tag_+e_buch")
    #     self.assertTrue(
    #         e_non_loan_applies(compound)
    #     )

        
    # def test_e_non_loan_is_applicable_1(self):
    #     compound = Compound("punkt_+e_stand")
    #     self.assertTrue(
    #         e_non_loan_is_applicable(compound)
    #     )

    # def test_e_non_loan_applies_1(self):
    #     compound = Compound("punkt_+e_stand")
    #     self.assertTrue(
    #         e_non_loan_applies(compound)
    #     )

        
    # def test_e_non_loan_is_applicable_2(self):
    #     compound = Compound("hund_+e_leine")
    #     self.assertTrue(
    #         e_non_loan_is_applicable(compound)
    #     )

    # def test_e_non_loan_applies_2(self):
    #     compound = Compound("hund_+e_leine")
    #     self.assertTrue(
    #         e_non_loan_applies(compound)
    #     )

        
    # def test_e_non_loan_is_applicable_3(self):
    #     compound = Compound("anhalt_+e_stelle")
    #     self.assertTrue(
    #         e_non_loan_is_applicable(compound)
    #     )

    # def test_e_non_loan_applies_3(self):
    #     compound = Compound("anhalt_+e_stelle")
    #     self.assertFalse(
    #         e_non_loan_applies(compound)
    #     )

        
    # def test_e_non_loan_is_applicable_4(self):
    #     compound = Compound("haus_tür")
    #     self.assertFalse(
    #         e_non_loan_is_applicable(compound)
    #     )

    # def test_e_non_loan_is_applicable_5(self):
    #     compound = Compound("dokument_+en_sammlung")
    #     self.assertFalse(
    #         e_non_loan_is_applicable(compound)
    #     )

    pass



class TestApplicabilityCheckersErPar(unittest.TestCase):

	# l2p:er|par
	#
    # All nouns that constitute first constituents that attach -(")er-
    # build the plural form with -(")er.

    def test_er_par_is_applicable_0(self):
        compound = Compound("buch_+=er_regal")
        self.assertTrue(
            er_par_is_applicable(compound)
        )

    def test_er_par_applies_0(self):
        compound = Compound("buch_+=er_regal")
        self.assertTrue(
            er_par_applies(compound)
        )

        
    def test_er_par_is_applicable_1(self):
        compound = Compound("kraut_+=er_frau")
        self.assertTrue(
            er_par_is_applicable(compound)
        )

    def test_er_par_applies_1(self):
        compound = Compound("kraut_+=er_frau")
        self.assertTrue(
            er_par_applies(compound)
        )

        
    def test_er_par_is_applicable_2(self):
        compound = Compound("kind_+=er_jacke")
        self.assertTrue(
            er_par_is_applicable(compound)
        )

    def test_er_par_applies_2(self):
        compound = Compound("kind_+=er_jacke")
        self.assertTrue(
            er_par_applies(compound)
        )

        
    def test_er_par_is_applicable_3(self):
        compound = Compound("haus_tür")
        self.assertFalse(
            er_par_is_applicable(compound)
        )

    def test_er_par_is_applicable_4(self):
        compound = Compound("blume_+n_topf")
        self.assertFalse(
            er_par_is_applicable(compound)
        )


class TestApplicabilityCheckersErLastSyl(unittest.TestCase):

	# l2p:er|#stressed_syl
	#
    # All nouns that constitute first constituents that attach -(")er-
    # have a stressed last syllable.

    def test_er_last_syl_is_applicable_0(self):
        compound = Compound("buch_+=er_regal")
        self.assertTrue(
            er_last_syl_is_applicable(compound)
        )

    def test_er_last_syl_applies_0(self):
        compound = Compound("buch_+=er_regal")
        self.assertTrue(
            er_last_syl_applies(compound)
        )

        
    def test_er_last_syl_is_applicable_1(self):
        compound = Compound("kraut_+=er_frau")
        self.assertTrue(
            er_last_syl_is_applicable(compound)
        )

    def test_er_last_syl_applies_1(self):
        compound = Compound("kraut_+=er_frau")
        self.assertTrue(
            er_last_syl_applies(compound)
        )

        
    def test_er_last_syl_is_applicable_2(self):
        compound = Compound("kind_+=er_jacke")
        self.assertTrue(
            er_last_syl_is_applicable(compound)
        )

    def test_er_last_syl_applies_2(self):
        compound = Compound("kind_+=er_jacke")
        self.assertTrue(
            er_last_syl_applies(compound)
        )

        
    def test_er_last_syl_is_applicable_3(self):
        compound = Compound("haus_tür")
        self.assertFalse(
            er_last_syl_is_applicable(compound)
        )

    def test_er_last_syl_is_applicable_4(self):
        compound = Compound("blume_+n_topf")
        self.assertFalse(
            er_last_syl_is_applicable(compound)
        )


    def test_er_last_syl_is_applicable_corr_0(self):
        compound = Compound("mitglied_+=er_liste")
        self.assertTrue(
            er_last_syl_is_applicable_corr(compound)
        )

    def test_er_last_syl_applies_corr_0(self):
        compound = Compound("mitglied_+=er_liste")
        self.assertTrue(
            er_last_syl_applies_corr(compound)
        )


class TestApplicabilityCheckersErSmpx(unittest.TestCase):

	# l2p:er|smpx
	#
    # Most nouns that constitute first constituents that attach -(")er-
    # are simplex.

    def test_er_smpx_is_applicable_0(self):
        compound = Compound("buch_+=er_regal")
        self.assertTrue(
            er_smpx_is_applicable(compound)
        )

    def test_er_smpx_applies_0(self):
        compound = Compound("buch_+=er_regal")
        self.assertTrue(
            er_smpx_applies(compound)
        )

        
    def test_er_smpx_is_applicable_1(self):
        compound = Compound("kraut_+=er_frau")
        self.assertTrue(
            er_smpx_is_applicable(compound)
        )

    def test_er_smpx_applies_1(self):
        compound = Compound("kraut_+=er_frau")
        self.assertTrue(
            er_smpx_applies(compound)
        )

        
    def test_er_smpx_is_applicable_2(self):
        compound = Compound("kind_+=er_jacke")
        self.assertTrue(
            er_smpx_is_applicable(compound)
        )

    def test_er_smpx_applies_2(self):
        compound = Compound("kind_+=er_jacke")
        self.assertTrue(
            er_smpx_applies(compound)
        )

        
    def test_er_smpx_is_applicable_3(self):
        compound = Compound("haus_tür")
        self.assertFalse(
            er_smpx_is_applicable(compound)
        )

    def test_er_smpx_is_applicable_4(self):
        compound = Compound("blume_+n_topf")
        self.assertFalse(
            er_smpx_is_applicable(compound)
        )


class TestApplicabilityCheckersErNonLoan(unittest.TestCase):

	# l2p:er|!loan
	#
    # All nouns that constitute first constituents that attach -(")er-
    # are native (none are loanwords).

    # def test_er_non_loan_is_applicable_0(self):
    #     compound = Compound("buch_+=er_regal")
    #     self.assertTrue(
    #         er_non_loan_is_applicable(compound)
    #     )

    # def test_er_non_loan_applies_0(self):
    #     compound = Compound("buch_+=er_regal")
    #     self.assertTrue(
    #         er_non_loan_applies(compound)
    #     )

        
    # def test_er_non_loan_is_applicable_1(self):
    #     compound = Compound("kraut_+=er_frau")
    #     self.assertTrue(
    #         er_non_loan_is_applicable(compound)
    #     )

    # def test_er_non_loan_applies_1(self):
    #     compound = Compound("kraut_+=er_frau")
    #     self.assertTrue(
    #         er_non_loan_applies(compound)
    #     )

        
    # def test_er_non_loan_is_applicable_2(self):
    #     compound = Compound("kind_+=er_jacke")
    #     self.assertTrue(
    #         er_non_loan_is_applicable(compound)
    #     )

    # def test_er_non_loan_applies_2(self):
    #     compound = Compound("kind_+=er_jacke")
    #     self.assertTrue(
    #         er_non_loan_applies(compound)
    #     )

        
    # def test_er_non_loan_is_applicable_3(self):
    #     compound = Compound("haus_tür")
    #     self.assertFalse(
    #         er_non_loan_is_applicable(compound)
    #     )

    # def test_er_non_loan_is_applicable_4(self):
    #     compound = Compound("blume_+n_topf")
    #     self.assertFalse(
    #         er_non_loan_is_applicable(compound)
    #     )

    pass



class TestApplicabilityCheckersEUlmPar(unittest.TestCase):

	# l2p:e_uml
	#
    # All nouns that constitute first constituents that attach -"e-
    # build the plural form with -e and umlaut.

    def test_e_uml_par_is_applicable_0(self):
        compound = Compound("hand_+=e_druck")
        self.assertTrue(
            e_uml_par_is_applicable(compound)
        )

    def test_e_uml_par_applies_0(self):
        compound = Compound("hand_+=e_druck")
        self.assertTrue(
            e_uml_par_applies(compound)
        )

        
    def test_e_uml_par_is_applicable_1(self):
        compound = Compound("arzt_+=e_streik")
        self.assertTrue(
            e_uml_par_is_applicable(compound)
        )

    def test_e_uml_par_applies_1(self):
        compound = Compound("arzt_+=e_streik")
        self.assertTrue(
            e_uml_par_applies(compound)
        )

        
    def test_e_uml_par_is_applicable_2(self):
        compound = Compound("gast_+=e_buch")
        self.assertTrue(
            e_uml_par_is_applicable(compound)
        )

    def test_e_uml_par_applies_2(self):
        compound = Compound("gast_+=e_buch")
        self.assertTrue(
            e_uml_par_applies(compound)
        )

        
    def test_e_uml_par_is_applicable_3(self):
        compound = Compound("blume_+e_topf")
        self.assertFalse(
            e_uml_par_is_applicable(compound)
        )

    def test_e_uml_par_is_applicable_4(self):
        compound = Compound("hund_+e_leine")
        self.assertFalse(
            e_uml_par_is_applicable(compound)
        )



class TestApplicabilityCheckersEsIsol:

	# l2p:es|isol
	#
    # All nouns that constitute first constituents that attach -es-
    # belong to a fixed row of masculine and neuter nouns and
    # build the genitive form with -(e)s-. -es- is thus isolated.

    # def test_es_isol_is_applicable_0(self):
    #     compound = Compound("bund_+es_tag")
    #     self.assertTrue(
    #         es_isol_is_applicable(compound)
    #     )

    # def test_es_isol_applies_0(self):
    #     compound = Compound("bund_+es_tag")
    #     self.assertTrue(
    #         es_isol_applies(compound)
    #     )

        
    # def test_es_isol_is_applicable_1(self):
    #     compound = Compound("kind_+es_alter")
    #     self.assertTrue(
    #         es_isol_is_applicable(compound)
    #     )

    # def test_es_isol_applies_1(self):
    #     compound = Compound("kind_+es_alter")
    #     self.assertTrue(
    #         es_isol_applies(compound)
    #     )

        
    # def test_es_isol_is_applicable_2(self):
    #     compound = Compound("tag_+es_schau")
    #     self.assertTrue(
    #         es_isol_is_applicable(compound)
    #     )

    # def test_es_isol_applies_2(self):
    #     compound = Compound("tag_+es_schau")
    #     self.assertTrue(
    #         es_isol_applies(compound)
    #     )

        
    # def test_es_isol_is_applicable_3(self):
    #     compound = Compound("land_+es_regierung")
    #     self.assertTrue(
    #         es_isol_is_applicable(compound)
    #     )

    # def test_es_isol_applies_3(self):
    #     compound = Compound("land_+es_regierung")
    #     self.assertTrue(
    #         es_isol_applies(compound)
    #     )

        
    # def test_es_isol_is_applicable_4(self):
    #     compound = Compound("kind_+er_garten")
    #     self.assertFalse(
    #         es_isol_is_applicable(compound)
    #     )

    # def test_es_isol_is_applicable_5(self):
    #     compound = Compound("land_kreis")
    #     self.assertFalse(
    #         es_isol_is_applicable(compound)
    #     )
        
    # def test_es_isol_is_applicable_6(self):
    #     compound = Compound("tag_blatt")
    #     self.assertFalse(
    #         es_isol_is_applicable(compound)
    #     )

	pass


class TestApplicabilityCheckersEsIsol(unittest.TestCase):

	# l2p:es|mono_syl
	#
    # All nouns that constitute first constituents that attach -es-
    # are monosyllabic.

    # def test_es_isol_is_applicable_0(self):
    #     compound = Compound("bund_+es_tag")   bund was removed from CELEX
    #     self.assertTrue(
    #         es_monosyl_is_applicable(compound)
    #     )

    # def test_es_monosyl_applies_0(self):
    #     compound = Compound("bund_+es_tag")
    #     self.assertTrue(
    #         es_monosyl_applies(compound)
    #     )

        
    def test_es_monosyl_is_applicable_1(self):
        compound = Compound("kind_+es_alter")
        self.assertTrue(
            es_monosyl_is_applicable(compound)
        )

    def test_es_monosyl_applies_1(self):
        compound = Compound("kind_+es_alter")
        self.assertTrue(
            es_monosyl_applies(compound)
        )

        
    def test_es_monosyl_is_applicable_2(self):
        compound = Compound("tag_+es_schau")
        self.assertTrue(
            es_monosyl_is_applicable(compound)
        )

    def test_es_monosyl_applies_2(self):
        compound = Compound("tag_+es_schau")
        self.assertTrue(
            es_monosyl_applies(compound)
        )

        
    def test_es_monosyl_is_applicable_3(self):
        compound = Compound("land_+es_regierung")
        self.assertTrue(
            es_monosyl_is_applicable(compound)
        )

    def test_es_monosyl_applies_3(self):
        compound = Compound("land_+es_regierung")
        self.assertTrue(
            es_monosyl_applies(compound)
        )

        
    def test_es_monosyl_is_applicable_4(self):
        compound = Compound("kind_+er_garten")
        self.assertFalse(
            es_monosyl_is_applicable(compound)
        )
        
    def test_es_monosyl_is_applicable_5(self):
        compound = Compound("land_kreis")
        self.assertFalse(
            es_monosyl_is_applicable(compound)
        )

    def test_es_isol_is_applicable_6(self):
        compound = Compound("tag_blatt")
        self.assertFalse(
            es_monosyl_is_applicable(compound)
        )


    def test_es_monosyl_is_applicable_corr_0(self):
        compound = Compound("vorjahr_+es_wagen")
        self.assertTrue(
            es_monosyl_is_applicable_corr(compound)
        )

    def test_es_monosyl_applies_corr_0(self):
        compound = Compound("vorjahr_+es_wagen")
        self.assertTrue(
            es_monosyl_applies_corr(compound)
        )


    def test_es_monosyl_is_applicable_corr_1(self):
        compound = Compound("bestand_+es_aufnahme")
        self.assertTrue(
            es_monosyl_is_applicable_corr(compound)
        )

    def test_es_monosyl_applies_corr_1(self):
        compound = Compound("bestand_+es_aufnahme")
        self.assertTrue(
            es_monosyl_applies_corr(compound)
        )



class TestApplicabilityCheckersEnsIsol:

	# l2p:ens
	#
    # All nouns that constitute first constituents that attach -(e)ns-
    # belong to a fixed group of a few masculine nouns and a single neuter noun
    # and have different genitive endings. -(e)ns- is thus isolated.

    # def test_ens_isol_is_applicable_0(self):
    #     compound = Compound("schmerz_+ens_geld")
    #     self.assertTrue(
    #         ens_isol_is_applicable(compound)
    #     )

    # def test_ens_isol_applies_0(self):
    #     compound = Compound("schmerz_+ens_geld")
    #     self.assertTrue(
    #         ens_isol_applies(compound)
    #     )

        
    # def test_ens_isol_is_applicable_1(self):
    #     compound = Compound("name_+ens_tag")
    #     self.assertTrue(
    #         ens_isol_is_applicable(compound)
    #     )

    # def test_ens_isol_applies_1(self):
    #     compound = Compound("name_+ens_tag")
    #     self.assertTrue(
    #         ens_isol_applies(compound)
    #     )

        
    # def test_ens_isol_is_applicable_2(self):
    #     compound = Compound("herz_+ens_angst")
    #     self.assertTrue(
    #         ens_isol_is_applicable(compound)
    #     )

    # def test_ens_isol_applies_2(self):
    #     compound = Compound("herz_+ens_angst")
    #     self.assertTrue(
    #         ens_isol_applies(compound)
    #     )

        
    # def test_ens_isol_is_applicable_3(self):
    #     compound = Compound("schmerz_grenze")
    #     self.assertTrue(
    #         ens_isol_is_applicable(compound)
    #     )

    # def test_ens_isol_applies_3(self):
    #     compound = Compound("schmerz_grenze")
    #     self.assertFalse(
    #         ens_isol_applies(compound)
    #     )

        
    # def test_ens_isol_is_applicable_4(self):
    #     compound = Compound("name_+n_buch")
    #     self.assertTrue(
    #         ens_isol_is_applicable(compound)
    #     )

    # def test_ens_isol_applies_4(self):
    #     compound = Compound("name_+n_buch")
    #     self.assertFalse(
    #         ens_isol_applies(compound)
    #     )

        
    # def test_ens_isol_is_applicable_5(self):
    #     compound = Compound("herz_leiden")
    #     self.assertTrue(
    #         ens_isol_is_applicable(compound)
    #     )

    # def test_ens_isol_applies_5(self):
    #     compound = Compound("herz_leiden")
    #     self.assertFalse(
    #         ens_isol_applies(compound)
    #     )

        
    # def test_ens_isol_is_applicable_6(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         ens_isol_is_applicable(compound)
    #     )

    # def test_ens_isol_is_applicable_7(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         ens_isol_is_applicable(compound)
    #     )

	pass



class TestApplicabilityCheckersZeroUmlPar(unittest.TestCase):

	# l2p:0_uml
	#
    # All nouns that constitute first constituents that attach a zero linker
    # with umlaut build the plural form with a zero ending and umlaut.

    def test_zero_uml_par_is_applicable_0(self):
        compound = Compound("bruder_+=_gemeinde")
        self.assertTrue(
            zero_uml_par_is_applicable(compound)
        )

    def test_zero_uml_par_applies_0(self):
        compound = Compound("bruder_+=_gemeinde")
        self.assertTrue(
            zero_uml_par_applies(compound)
        )

        
    def test_zero_uml_par_is_applicable_1(self):
        compound = Compound("mutter_+=_zentrum")
        self.assertTrue(
            zero_uml_par_is_applicable(compound)
        )

    def test_zero_uml_par_applies_1(self):
        compound = Compound("mutter_+=_zentrum")
        self.assertTrue(
            zero_uml_par_applies(compound)
        )

        
    def test_zero_uml_par_is_applicable_2(self):
        compound = Compound("vater_+=_aufbruch")
        self.assertTrue(
            zero_uml_par_is_applicable(compound)
        )

    def test_zero_uml_par_applies_2(self):
        compound = Compound("vater_+=_aufbruch")
        self.assertTrue(
            zero_uml_par_applies(compound)
        )

        
    def test_zero_uml_par_is_applicable_3(self):
        compound = Compound("brötchen_geber")
        self.assertFalse(
            zero_uml_par_is_applicable(compound)
        )

    def test_zero_uml_par_is_applicable_4(self):
        compound = Compound("haus_tür")
        self.assertFalse(
            zero_uml_par_is_applicable(compound)
        )



class TestApplicabilityCheckersPlInterpr:

	# p2l:tend:pl_interpr-pl_marker|def-pl_marker
	#
    # Linkers that are identical to the plural ending
    # of the first constituent in a given compound
    # tend to be associated with
    # a plural meaning of this first constituent within the compound.

    # def test_pl_interpr_is_applicable_0(self):
    #     compound = Compound("punkt_+e_stand")
    #     self.assertTrue(
    #         pl_interpr_is_applicable(compound)
    #     )

    # def test_pl_interpr_applies_0(self):
    #     compound = Compound("punkt_+e_stand")
    #     self.assertTrue(
    #         pl_interpr_applies(compound)
    #     )

        
    # def test_pl_interpr_is_applicable_1(self):
    #     compound = Compound("buch_+=er_regal")
    #     self.assertTrue(
    #         pl_interpr_is_applicable(compound)
    #     )

    # def test_pl_interpr_applies_1(self):
    #     compound = Compound("buch_+=er_regal")
    #     self.assertTrue(
    #         pl_interpr_applies(compound)
    #     )

        
    # def test_pl_interpr_is_applicable_2(self):
    #     compound = Compound("staat_+en_bund")
    #     self.assertTrue(
    #         pl_interpr_is_applicable(compound)
    #     )

    # def test_pl_interpr_applies_2(self):
    #     compound = Compound("staat_+en_bund")
    #     self.assertTrue(
    #         pl_interpr_applies(compound)
    #     )

        
    # def test_pl_interpr_is_applicable_3(self):
    #     compound = Compound("burg_+en_land")
    #     self.assertTrue(
    #         pl_interpr_is_applicable(compound)
    #     )

    # def test_pl_interpr_applies_3(self):
    #     compound = Compound("burg_+en_land")
    #     self.assertTrue(
    #         pl_interpr_applies(compound)
    #     )

        
    # def test_pl_interpr_is_applicable_4(self):
    #     compound = Compound("mutter_+=_zentrum")
    #     self.assertTrue(
    #         pl_interpr_is_applicable(compound)
    #     )

    # def test_pl_interpr_applies_4(self):
    #     compound = Compound("mutter_+=_zentrum")
    #     self.assertTrue(
    #         pl_interpr_applies(compound)
    #     )

        
    # def test_pl_interpr_is_applicable_5(self):
    #     compound = Compound("pilz_sammler")
    #     self.assertTrue(
    #         pl_interpr_is_applicable(compound)
    #     )

    # def test_pl_interpr_applies_5(self):
    #     compound = Compound("pilz_sammler")
    #     self.assertFalse(
    #         pl_interpr_applies(compound)
    #     )

        
    # def test_pl_interpr_is_applicable_6(self):
    #     compound = Compound("buch_handel")
    #     self.assertTrue(
    #         pl_interpr_is_applicable(compound)
    #     )

    # def test_pl_interpr_applies_6(self):
    #     compound = Compound("buch_handel")
    #     self.assertFalse(
    #         pl_interpr_applies(compound)
    #     )

        
    # def test_pl_interpr_is_applicable_7(self):
    #     compound = Compound("motor_+en_geräusch")
    #     self.assertTrue(
    #         pl_interpr_is_applicable(compound)
    #     )

    # def test_pl_interpr_applies_7(self):
    #     compound = Compound("motor_+en_geräusch")
    #     self.assertFalse(
    #         pl_interpr_applies(compound)
    #     )

        
    # def test_pl_interpr_is_applicable_8(self):
    #     compound = Compound("burg_+en_blick")
    #     self.assertTrue(
    #         pl_interpr_is_applicable(compound)
    #     )

    # def test_pl_interpr_applies_8(self):
    #     compound = Compound("burg_+en_blick")
    #     self.assertFalse(
    #         pl_interpr_applies(compound)
    #     )

        
    # def test_pl_interpr_is_applicable_9(self):
    #     compound = Compound("vogel_futter")
    #     self.assertTrue(
    #         pl_interpr_is_applicable(compound)
    #     )

    # def test_pl_interpr_applies_9(self):
    #     compound = Compound("vogel_futter")
    #     self.assertFalse(
    #         pl_interpr_applies(compound)
    #     )

        
    # def test_pl_interpr_is_applicable_10(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         pl_interpr_is_applicable(compound)
    #     )

    # def test_pl_interpr_is_applicable_11(self):
    #     compound = Compound("TODO")
    #     self.assertFalse(
    #         pl_interpr_is_applicable(compound)
    #     )

	pass



if __name__ == '__main__':
    unittest.main()