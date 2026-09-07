import unittest

from data_utils.gecodb_compound_parser import Compound
from data_utils.germanet_search import germanet
from check_applicability.l2p_satisfaction_checkers import *
from check_applicability.l2p_satisfaction_checkers import (
    _is_of_plural,
    _has_no_plural,
    _is_of_gender,
    _is_simplex,
    _is_derived,
    _is_prefixed,
    _phone_has_property,
    _is_vowel,
    _ends_with_phon,
    _ends_with_phon_schwa,
    _has_n_syllables,
    _is_monosyllabic,
    _is_syl_stressed,
    _is_trochaic,
    _is_last_syl_stressed,
    _is_of_catergory
)


# Tests for helper functions

class TestIsOfPlural(unittest.TestCase):

    # def test_is_of_zero_plural_00(self):
    #     self.assertTrue(
    #         _is_of_zero_plural("teufel")
    #     )

    def test_is_of_zero_plural_01(self):
        self.assertFalse(
            _is_of_plural("teufel", "s")
        )


    # def test_is_of_zero_plural_10(self):
    #     self.assertTrue(
    #         _is_of_zero_plural("essen")
    #     )

    def test_is_of_zero_plural_11(self):
        self.assertFalse(
            _is_of_plural("essen", "n")
        )


    def test_is_of_plural_00(self):
        self.assertTrue(
            _is_of_plural("frage", "en")
        )

    # def test_is_of_plural_01(self):
    #     self.assertFalse(
    #         _is_of_zero_plural("frage")
    #     )


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
        # to investigate the effect of the umlaut on
        # plural effect, we disambiguate between -"er- and -er-
        # in this version
        self.assertTrue(
            _is_of_plural("kind", "er", adds_umlaut=False)
        )

    def test_is_of_plural_31(self):
        self.assertFalse(
            _is_of_plural("kind", "er", adds_umlaut=True)
        )


    def test_is_of_plural_40(self):
        self.assertTrue(
            _is_of_plural("vogel", "", adds_umlaut=True)
        )

    # def test_is_of_plural_41(self):
    #     self.assertFalse(
    #         _is_of_zero_plural("vogel")
    #     )


    def test_is_of_plural_50(self):
        self.assertTrue(
            _is_of_plural("auto", "s")
        )

    # def test_is_of_plural_51(self):
    #     self.assertFalse(
    #         _is_of_zero_plural("auto")
    #     )


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
            _is_of_plural("licht", "er", adds_umlaut=False)
        )

    def test_is_multiple_plural_12(self):
        self.assertFalse(
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


class TestIsOfCategory(unittest.TestCase):

    _lexunits = {
        "hund": "l71772",
        "insekt": "l70037",
        "bakterie": "l72079",
        "person": "l140806",
        "könig": "l48811",
        "stern": "l62501",
        "mond": "l62503",
        "wind": "l60380",
        "mai": "l72659",
        "montag": "l72745",
        "glas_m": "l68144",
        "glas_a": "l9711"
    }

    def _get_lu(self, lemma: str) -> Lexunit:
        return germanet.get_lexunit_by_id(
            self._lexunits[lemma]
        )


    def test_animal_0(self):
        lemma = self._get_lu("hund")
        cats = "animal"
        self.assertTrue(_is_of_catergory(lemma, cats))

    def test_animal_1(self):
        lemma = self._get_lu("insekt")
        cats = "animal"
        self.assertTrue(_is_of_catergory(lemma, cats))

    def test_animal_2(self):
        lemma = self._get_lu("bakterie")
        cats = ["animal"]
        self.assertFalse(_is_of_catergory(lemma, cats))


    def test_person_0(self):
        lemma = self._get_lu("person")
        cats = "person"
        self.assertTrue(_is_of_catergory(lemma, cats))

    def test_person_1(self):
        lemma = self._get_lu("könig")
        cats = ["person"]
        self.assertTrue(_is_of_catergory(lemma, cats))

    def test_person_2(self):
        lemma = self._get_lu("hund")
        cats = "person"
        self.assertFalse(_is_of_catergory(lemma, cats))


    def test_astronomic_obj_0(self):
        lemma = self._get_lu("stern")
        cats = ["astronomic_obj"]
        self.assertTrue(_is_of_catergory(lemma, cats))

    def test_astronomic_obj_1(self):
        lemma = self._get_lu("mond")
        cats = "astronomic_obj"
        self.assertTrue(_is_of_catergory(lemma, cats))

    def test_astronomic_obj_2(self):
        lemma = self._get_lu("wind")
        cats = "astronomic_obj"
        self.assertFalse(_is_of_catergory(lemma, cats))


    def test_month_0(self):
        lemma = self._get_lu("mai")
        cats = "month"
        self.assertTrue(_is_of_catergory(lemma, cats))

    def test_month_2(self):
        lemma = self._get_lu("montag")
        cats = ["month"]
        self.assertFalse(_is_of_catergory(lemma, cats))


    def test_mass_0(self):
        lemma = self._get_lu("glas_m")
        cats = ["mass"]
        self.assertTrue(_is_of_catergory(lemma, cats))

    def test_mass_1(self):
        lemma = self._get_lu("glas_a")
        cats = "mass"
        self.assertFalse(_is_of_catergory(lemma, cats))


    def test_mixed_0(self):
        lemma = self._get_lu("könig")
        cats = ["animal", "person"]
        self.assertTrue(_is_of_catergory(lemma, cats))

    def test_mixed_1(self):
        lemma = self._get_lu("mai")
        cats = ["person", "astronomic_obj", "month"]
        self.assertTrue(_is_of_catergory(lemma, cats))

    def test_mixed_2(self):
        lemma = self._get_lu("mai")
        cats = ["person", "astronomic_obj"]
        self.assertFalse(_is_of_catergory(lemma, cats))


    def test_key_error_0(self):
        lemma = self._get_lu("hund")
        cats = ["animal", "mammal"]
        with self.assertRaises(KeyError):
            _ = _is_of_catergory(lemma, cats)

    def test_key_error_1(self):
        lemma = self._get_lu("hund")
        cats = "person, animal"
        with self.assertRaises(KeyError):
            _ = _is_of_catergory(lemma, cats)
    


# Tests for L2P satisfaction checkers

class TestApplicabilityCheckersCmpxMorph(unittest.TestCase):

	# l2p:s|tend_cmpx_morph
	#
    # The probability of -s- grows irregularly with the
    # morphological complexity of the first constituent
    # (any form of derivation).

    def test_cmpx_morph_is_presatisfied_0(self):
        compound = Compound("gesundheit_+s_amt")
        self.assertTrue(
            cmpx_morph_is_presatisfied(compound)
        )

    def test_cmpx_morph_is_satisfied_0(self):
        compound = Compound("gesundheit_+s_amt")
        self.assertTrue(
            cmpx_morph_is_satisfied(compound)
        )

        
    def test_cmpx_morph_is_presatisfied_1(self):
        compound = Compound("gesellschaft_+s_politik")
        self.assertTrue(
            cmpx_morph_is_presatisfied(compound)
        )

    def test_cmpx_morph_is_satisfied_1(self):
        compound = Compound("gesellschaft_+s_politik")
        self.assertTrue(
            cmpx_morph_is_satisfied(compound)
        )

        
    def test_cmpx_morph_is_presatisfied_2(self):
        compound = Compound("anspruch_+s_haltung")
        self.assertTrue(
            cmpx_morph_is_presatisfied(compound)
        )

    def test_cmpx_morph_is_satisfied_2(self):
        compound = Compound("anspruch_+s_haltung")
        self.assertTrue(
            cmpx_morph_is_satisfied(compound)
        )

        
    def test_cmpx_morph_is_presatisfied_3(self):
        compound = Compound("eintrag_+s_frist")
        self.assertTrue(
            cmpx_morph_is_presatisfied(compound)
        )

    def test_cmpx_morph_is_satisfied_3(self):
        compound = Compound("eintrag_+s_frist")
        self.assertTrue(
            cmpx_morph_is_satisfied(compound)
        )


    def test_cmpx_morph_is_presatisfied_4(self):
        compound = Compound("ort_+s_amt")
        self.assertTrue(
            cmpx_morph_is_presatisfied(compound)
        )

    def test_cmpx_morph_is_satisfied_4(self):
        compound = Compound("ort_+s_amt")
        self.assertFalse(
            cmpx_morph_is_satisfied(compound)
        )


    def test_cmpx_morph_is_presatisfied_5(self):
        compound = Compound("krieg_+s_ende")
        self.assertTrue(
            cmpx_morph_is_presatisfied(compound)
        )

    def test_cmpx_morph_is_satisfied_5(self):
        compound = Compound("krieg_+s_ende")
        self.assertFalse(
            cmpx_morph_is_satisfied(compound)
        )

        
    def test_cmpx_morph_is_presatisfied_6(self):
        compound = Compound("minderheit_+en_recht")
        self.assertTrue(
            cmpx_morph_is_presatisfied(compound)
        )

    def test_cmpx_morph_is_satisfied_6(self):
        compound = Compound("minderheit_+en_recht")
        self.assertTrue(
            cmpx_morph_is_satisfied(compound)
        )


    def test_cmpx_morph_is_presatisfied_7(self):
        compound = Compound("hund_+e_leine")
        self.assertTrue(
            cmpx_morph_is_presatisfied(compound)
        )

    def test_cmpx_morph_is_satisfied_7(self):
        compound = Compound("hund_+e_leine")
        self.assertFalse(
            cmpx_morph_is_satisfied(compound)
        )


class TestApplicabilityCheckersCmpxPhon(unittest.TestCase):

	# l2p:s|tend_cmpx_phon
	#
    # The probability of -s- grows irregularly with the
    # phonological complexity of the first constituent.
    # By phonologically complex words are understood
    # words with polysyllable non-trochaic form,
    # words with unstressed prefixes,
    # words with stressed or semi-stressed suffixes etc.

    def test_cmpx_phon_is_presatisfied_0(self):
        compound = Compound("beruf_+s_erfahrung")
        self.assertTrue(
            cmpx_phon_is_presatisfied(compound)
        )

    def test_cmpx_phon_is_satisfied_0(self):
        compound = Compound("beruf_+s_erfahrung")
        self.assertTrue(
            cmpx_phon_is_satisfied(compound)
        )

        
    def test_cmpx_phon_is_presatisfied_1(self):
        compound = Compound("religion_+s_unterricht")
        self.assertTrue(
            cmpx_phon_is_presatisfied(compound)
        )

    def test_cmpx_phon_is_satisfied_1(self):
        compound = Compound("religion_+s_unterricht")
        self.assertTrue(
            cmpx_phon_is_satisfied(compound)
        )

        
    def test_cmpx_phon_is_presatisfied_2(self):
        compound = Compound("liebe_+s_brief")
        self.assertTrue(
            cmpx_phon_is_presatisfied(compound)
        )

    def test_cmpx_phon_is_satisfied_2(self):
        compound = Compound("liebe_+s_brief")
        self.assertFalse(
            cmpx_phon_is_satisfied(compound)
        )

        
    def test_cmpx_phon_is_presatisfied_3(self):
        compound = Compound("land_+s_mann")
        self.assertTrue(
            cmpx_phon_is_presatisfied(compound)
        )

    def test_cmpx_phon_is_satisfied_3(self):
        compound = Compound("land_+s_mann")
        self.assertFalse(
            cmpx_phon_is_satisfied(compound)
        )


    def test_cmpx_phon_is_presatisfied_4(self):
        compound = Compound("hund_+e_leine")
        self.assertTrue(
            cmpx_phon_is_presatisfied(compound)
        )

    def test_cmpx_phon_is_satisfied_4(self):
        compound = Compound("hund_+e_leine")
        self.assertFalse(
            cmpx_phon_is_satisfied(compound)
        )


class TestApplicabilityCheckersSonority(unittest.TestCase):

	# l2p:s|tend_!sonority
	#
    # The probability of -s- in compounds with simplex first constituents
    # tends to decrease with the increasing sonority of the final segment
    # of the first constituent. -s- is thus more frequent after plosives,
    # infrequent after nasals and liquids,
    # and it never occurs after a full vowel.

    def test_sonority_is_presatisfied_0(self):
        compound = Compound("ort_+s_tarif")
        self.assertTrue(
            sonority_is_presatisfied(compound)
        )

    def test_sonority_is_satisfied_0(self):
        compound = Compound("ort_+s_tarif")
        self.assertTrue(
            sonority_is_satisfied(compound)
        )

        
    def test_sonority_is_presatisfied_1(self):
        compound = Compound("glück_+s_rad")
        self.assertTrue(
            sonority_is_presatisfied(compound)
        )

    def test_sonority_is_satisfied_1(self):
        compound = Compound("glück_+s_rad")
        self.assertTrue(
            sonority_is_satisfied(compound)
        )

        
    def test_sonority_is_presatisfied_2(self):
        compound = Compound("land_+s_mann")
        self.assertTrue(
            sonority_is_presatisfied(compound)
        )

    def test_sonority_is_satisfied_2(self):
        compound = Compound("land_+s_mann")
        self.assertTrue(
            sonority_is_satisfied(compound)
        )


    def test_sonority_is_presatisfied_3(self):
        compound = Compound("himmel_+s_bahn")
        self.assertTrue(
            sonority_is_presatisfied(compound)
        )

    def test_sonority_is_satisfied_3(self):
        compound = Compound("himmel_+s_bahn")
        self.assertFalse(
            sonority_is_satisfied(compound)
        )


    # def test_sonority_is_presatisfied_4(self):
    #     compound = Compound("liebe_+s_brief")
    #     self.assertTrue(
    #         sonority_is_presatisfied(compound)
    #     )

    # def test_sonority_is_satisfied_4(self):
    #     compound = Compound("liebe_+s_brief")
    #     self.assertFalse(
    #         sonority_is_satisfied(compound)
    #     )

        
    def test_sonority_is_presatisfied_5(self):
        compound = Compound("uhu_+s_nest")
        self.assertTrue(
            sonority_is_presatisfied(compound)
        )

    def test_sonority_is_satisfied_5(self):
        compound = Compound("uhu_+s_nest")
        self.assertFalse(
            sonority_is_satisfied(compound)
        )


    def test_sonority_is_presatisfied_6(self):
        compound = Compound("gefäß_system")
        self.assertFalse(
            sonority_is_presatisfied(compound)
        )

    def test_sonority_is_presatisfied_7(self):
        compound = Compound("beruf_+s_erfahrung")
        self.assertFalse(
            sonority_is_presatisfied(compound)
        )


class TestApplicabilityCheckersSSmpx(unittest.TestCase):

	# l2p:s|smpx_mn
	#
    # All except for a few simplex nouns that constitute first constituents
    # that attach -s- belong to a small fixed group
    # of masculine and neuter nouns.

    def test_s_smpx_is_presatisfied_0(self):
        compound = Compound("amt_+s_leiter")
        self.assertTrue(
            s_smpx_is_presatisfied(compound)
        )

    def test_s_smpx_is_satisfied_0(self):
        compound = Compound("amt_+s_leiter")
        self.assertTrue(
            s_smpx_is_satisfied(compound)
        )

        
    def test_s_smpx_is_presatisfied_1(self):
        compound = Compound("hund_+e_leine")
        self.assertTrue(
            s_smpx_is_presatisfied(compound)
        )

    def test_s_smpx_is_satisfied_1(self):
        compound = Compound("hund_+e_leine")
        self.assertTrue(
            s_smpx_is_satisfied(compound)
        )

        
    def test_s_smpx_is_presatisfied_2(self):
        compound = Compound("arbeit_+s_amt")
        self.assertTrue(
            s_smpx_is_presatisfied(compound)
        )

    def test_s_smpx_is_satisfied_2(self):
        compound = Compound("arbeit_+s_amt")
        self.assertFalse(
            s_smpx_is_satisfied(compound)
        )

        
    def test_s_smpx_is_presatisfied_3(self):
        compound = Compound("beruf_+s_erfahrung")
        self.assertFalse(
            s_smpx_is_presatisfied(compound)
        )


class TestApplicabilityCheckersSFreq(unittest.TestCase):

	# l2p:s|smpx_high_freq
	#
    # Many simplex nouns that constitute first constituents
    # that attach -s- have a high token frequency.

    def test_s_freq_is_presatisfied_0(self):
        compound = Compound("volk_+s_brauch")
        self.assertTrue(
            s_freq_is_presatisfied(compound)
        )

    def test_s_freq_is_satisfied_0(self):
        compound = Compound("volk_+s_brauch")
        self.assertTrue(
            s_freq_is_satisfied(compound)
        )

        
    def test_s_freq_is_presatisfied_1(self):
        compound = Compound("hund_+e_leine")
        self.assertTrue(
            s_freq_is_presatisfied(compound)
        )

    def test_s_freq_is_satisfied_1(self):
        compound = Compound("hund_+e_leine")
        self.assertTrue(
            s_freq_is_satisfied(compound)
        )


    def test_s_freq_is_presatisfied_2(self):
        compound = Compound("aal_suppe")
        self.assertTrue(
            s_freq_is_presatisfied(compound)
        )
    
    def test_s_freq_is_satisfied_2(self):
        compound = Compound("aal_suppe")
        self.assertFalse(
            s_freq_is_satisfied(compound)
        )

        
    def test_s_freq_is_presatisfied_3(self):
        compound = Compound("beruf_+s_erfahrung")
        self.assertFalse(
            s_freq_is_presatisfied(compound)
        )


class TestApplicabilityCheckersSFCmpx(unittest.TestCase):

	# l2p:s|f_cmpx
	#
    # Almost all feminine nouns that constitute first constituents
    # that attach -s- are morphologically complex.

    def test_s_f_cmpx_is_presatisfied_0(self):
        compound = Compound("gesundheit_+s_amt")
        self.assertTrue(
            s_f_cmpx_is_presatisfied(compound)
        )

    def test_s_f_cmpx_is_satisfied_0(self):
        compound = Compound("gesundheit_+s_amt")
        self.assertTrue(
            s_f_cmpx_is_satisfied(compound)
        )

        
    def test_s_f_cmpx_is_presatisfied_1(self):
        compound = Compound("generation_+en_konflikt")
        self.assertTrue(
            s_f_cmpx_is_presatisfied(compound)
        )

    def test_s_f_cmpx_is_satisfied_1(self):
        compound = Compound("generation_+en_konflikt")
        self.assertTrue(
            s_f_cmpx_is_satisfied(compound)
        )


    def test_s_f_cmpx_is_presatisfied_2(self):
        compound = Compound("arbeit_+s_tag")
        self.assertTrue(
            s_f_cmpx_is_presatisfied(compound)
        )

    def test_s_f_cmpx_is_satisfied_2(self):
        compound = Compound("arbeit_+s_tag")
        self.assertFalse(
            s_f_cmpx_is_satisfied(compound)
        )

        
    def test_s_f_cmpx_is_presatisfied_3(self):
        compound = Compound("ort_+s_amt")
        self.assertFalse(
            s_f_cmpx_is_presatisfied(compound)
        )


class TestApplicabilityCheckersSFPolysyl(unittest.TestCase):

	# l2p:s|f_poly_syl
	#
    # Almost all feminine nouns that constitute first constituents
    # that attach -s- are polysyllabic.

    def test_s_f_polysyl_is_presatisfied_0(self):
        compound = Compound("gesundheit_+s_amt")
        self.assertTrue(
            s_f_polysyl_is_presatisfied(compound)
        )

    def test_s_f_polysyl_is_satisfied_0(self):
        compound = Compound("gesundheit_+s_amt")
        self.assertTrue(
            s_f_polysyl_is_satisfied(compound)
        )

        
    def test_s_f_polysyl_is_presatisfied_1(self):
        compound = Compound("generation_+en_konflikt")
        self.assertTrue(
            s_f_polysyl_is_presatisfied(compound)
        )

    def test_s_f_polysyl_is_satisfied_1(self):
        compound = Compound("generation_+en_konflikt")
        self.assertTrue(
            s_f_polysyl_is_satisfied(compound)
        )

        
    def test_s_f_polysyl_is_presatisfied_2(self):
        compound = Compound("ort_+s_amt")
        self.assertFalse(
            s_f_polysyl_is_presatisfied(compound)
        )



class TestApplicabilityCheckersEnPar(unittest.TestCase):

	# l2p:en|par
	#
    # All nouns that constitute first constituents
    # that attach -(e)n- belong are weak nouns.

    def test_en_par_is_presatisfied_0(self):
        compound = Compound("blume_+n_topf")
        self.assertTrue(
            en_par_is_presatisfied(compound)
        )

    def test_en_par_is_satisfied_0(self):
        compound = Compound("blume_+n_topf")
        self.assertTrue(
            en_par_is_satisfied(compound)
        )

        
    def test_en_par_is_presatisfied_2(self):
        compound = Compound("hund_+e_leine")
        self.assertTrue(
            en_par_is_presatisfied(compound)
        )

    def test_en_par_is_satisfied_2(self):
        compound = Compound("hund_+e_leine")
        self.assertFalse(
            en_par_is_satisfied(compound)
        )


class TestApplicabilityCheckersEnNonParM(unittest.TestCase):

	# l2p:en|non_par_m
	#
    # All masculine nouns that do not build the plural form with -(e)n
    # that constitute first constituents that attach -(e)n-
    # are monosyllabic designations of male persons, animals,
    # astronomic objects, months.

    def test_en_non_par_m_is_presatisfied_0(self):
        compound = Compound("hahn_+en_kamm")
        self.assertTrue(
            en_non_par_m_is_presatisfied(compound)
        )

    def test_en_non_par_m_is_satisfied_0(self):
        compound = Compound("hahn_+en_kamm")
        self.assertTrue(
            en_non_par_m_is_satisfied(compound)
        )

        
    def test_en_non_par_m_is_presatisfied_1(self):
        compound = Compound("stern_karte")
        self.assertTrue(
            en_non_par_m_is_presatisfied(compound)
        )

    def test_en_non_par_m_is_satisfied_1(self):
        compound = Compound("stern_karte")
        self.assertTrue(
            en_non_par_m_is_satisfied(compound)
        )
        

    def test_en_non_par_m_is_presatisfied_2(self):
        compound = Compound("instrument_+en_bau")
        self.assertFalse(
            en_non_par_m_is_presatisfied(compound)
        )



class TestApplicabilityCheckersEPar(unittest.TestCase):

	# l2p:e|par
	#
    # All nouns that constitute first constituents that attach -e-
    # build the plural form with -e.

    def test_e_par_is_presatisfied_0(self):
        compound = Compound("tag_+e_buch")
        self.assertTrue(
            e_par_is_presatisfied(compound)
        )

    def test_e_par_is_satisfied_0(self):
        compound = Compound("tag_+e_buch")
        self.assertTrue(
            e_par_is_satisfied(compound)
        )


    def test_e_par_is_presatisfied_1(self):
        compound = Compound("haus_tür")
        self.assertTrue(
            e_par_is_presatisfied(compound)
        )

    def test_e_par_is_satisfied_1(self):
        compound = Compound("haus_tür")
        self.assertFalse(
            e_par_is_satisfied(compound)
        )


class TestApplicabilityCheckersELastSyl(unittest.TestCase):

	# l2p:e|#stressed_syl
	#
    # All nouns that constitute first constituents that attach -e-
    # have a stressed last syllable or are derived of those with a stressed prefix.

    def test_e_last_syl_is_presatisfied_0(self):
        compound = Compound("tag_+e_buch")
        self.assertTrue(
            e_last_syl_is_presatisfied(compound)
        )

    def test_e_last_syl_is_satisfied_0(self):
        compound = Compound("tag_+e_buch")
        self.assertTrue(
            e_last_syl_is_satisfied(compound)
        )

        
    def test_e_last_syl_is_presatisfied_1(self):
        compound = Compound("kind_+er_jacke")
        self.assertTrue(
            e_last_syl_is_presatisfied(compound)
        )

    def test_e_last_syl_is_satisfied_1(self):
        compound = Compound("kind_+er_jacke")
        self.assertTrue(
            e_last_syl_is_satisfied(compound)
        )


class TestApplicabilityCheckersESmpx(unittest.TestCase):

	# l2p:e|smpx
	#
    # Most nouns that constitute first constituents that attach -e- are simplex.

    def test_e_smpx_is_presatisfied_0(self):
        compound = Compound("tag_+e_buch")
        self.assertTrue(
            e_smpx_is_presatisfied(compound)
        )

    def test_e_smpx_is_satisfied_0(self):
        compound = Compound("tag_+e_buch")
        self.assertTrue(
            e_smpx_is_satisfied(compound)
        )

        
    def test_e_smpx_is_presatisfied_1(self):
        compound = Compound("kind_+er_jacke")
        self.assertTrue(
            e_smpx_is_presatisfied(compound)
        )

    def test_e_smpx_is_satisfied_1(self):
        compound = Compound("kind_+er_jacke")
        self.assertTrue(
            e_smpx_is_satisfied(compound)
        )

        
    def test_e_smpx_is_presatisfied_2(self):
        compound = Compound("anhalt_+e_stelle")
        self.assertTrue(
            e_smpx_is_presatisfied(compound)
        )

    def test_e_smpx_is_satisfied_2(self):
        compound = Compound("anhalt_+e_stelle")
        self.assertFalse(
            e_smpx_is_satisfied(compound)
        )



class TestApplicabilityCheckersErPar(unittest.TestCase):

	# l2p:er|par
	#
    # All nouns that constitute first constituents that attach -(")er-
    # build the plural form with -(")er.

    def test_er_par_is_presatisfied_0(self):
        compound = Compound("buch_+=er_regal")
        self.assertTrue(
            er_par_is_presatisfied(compound)
        )

    def test_er_par_is_satisfied_0(self):
        compound = Compound("buch_+=er_regal")
        self.assertTrue(
            er_par_is_satisfied(compound)
        )

        
    def test_er_par_is_presatisfied_1(self):
        compound = Compound("hund_+e_leine")
        self.assertTrue(
            er_par_is_presatisfied(compound)
        )

    def test_er_par_is_satisfied_1(self):
        compound = Compound("hund_+e_leine")
        self.assertFalse(
            er_par_is_satisfied(compound)
        )


class TestApplicabilityCheckersErLastSyl(unittest.TestCase):

	# l2p:er|#stressed_syl
	#
    # All nouns that constitute first constituents that attach -(")er-
    # have a stressed last syllable or are derived of those with a stressed prefix.

    def test_er_last_syl_is_presatisfied_0(self):
        compound = Compound("buch_+=er_regal")
        self.assertTrue(
            er_last_syl_is_presatisfied(compound)
        )

    def test_er_last_syl_is_satisfied_0(self):
        compound = Compound("buch_+=er_regal")
        self.assertTrue(
            er_last_syl_is_satisfied(compound)
        )

        
    def test_er_last_syl_is_presatisfied_0(self):
        compound = Compound("hund_+e_leine")
        self.assertTrue(
            er_last_syl_is_presatisfied(compound)
        )

    def test_er_last_syl_is_satisfied_0(self):
        compound = Compound("hund_+e_leine")
        self.assertTrue(
            er_last_syl_is_satisfied(compound)
        )


    def test_er_last_syl_is_presatisfied_0(self):
        compound = Compound("blume_+n_topf")
        self.assertTrue(
            er_last_syl_is_presatisfied(compound)
        )

    def test_er_last_syl_is_satisfied_0(self):
        compound = Compound("blume_+n_topf")
        self.assertFalse(
            er_last_syl_is_satisfied(compound)
        )


class TestApplicabilityCheckersErSmpx(unittest.TestCase):

	# l2p:er|smpx
	#
    # Most nouns that constitute first constituents that attach -(")er-
    # are simplex.

    def test_er_smpx_is_presatisfied_0(self):
        compound = Compound("buch_+=er_regal")
        self.assertTrue(
            er_smpx_is_presatisfied(compound)
        )

    def test_er_smpx_is_satisfied_0(self):
        compound = Compound("buch_+=er_regal")
        self.assertTrue(
            er_smpx_is_satisfied(compound)
        )

    def test_er_smpx_is_presatisfied_1(self):
        compound = Compound("hund_+e_leine")
        self.assertTrue(
            er_smpx_is_presatisfied(compound)
        )

    def test_er_smpx_is_satisfied_1(self):
        compound = Compound("hund_+e_leine")
        self.assertTrue(
            er_smpx_is_satisfied(compound)
        )


    def test_er_smpx_is_presatisfied_2(self):
        compound = Compound("mitglied_+er_liste")
        self.assertTrue(
            er_smpx_is_presatisfied(compound)
        )

    def test_er_smpx_is_satisfied_2(self):
        compound = Compound("mitglied_+er_liste")
        self.assertFalse(
            er_smpx_is_satisfied(compound)
        )



class TestApplicabilityCheckersEUlmPar(unittest.TestCase):

	# l2p:e_uml
	#
    # All nouns that constitute first constituents that attach -"e-
    # build the plural form with -e and umlaut.

    def test_e_uml_par_is_presatisfied_0(self):
        compound = Compound("hand_+=e_druck")
        self.assertTrue(
            e_uml_par_is_presatisfied(compound)
        )

    def test_e_uml_par_is_satisfied_0(self):
        compound = Compound("hand_+=e_druck")
        self.assertTrue(
            e_uml_par_is_satisfied(compound)
        )


    def test_e_uml_par_is_presatisfied_1(self):
        compound = Compound("blume_+n_topf")
        self.assertTrue(
            e_uml_par_is_presatisfied(compound)
        )

    def test_e_uml_par_is_satisfied_1(self):
        compound = Compound("blume_+n_topf")
        self.assertFalse(
            e_uml_par_is_satisfied(compound)
        )


class TestApplicabilityCheckersEsMonosyl(unittest.TestCase):
        
    def test_es_monosyl_is_presatisfied_0(self):
        compound = Compound("kind_+es_alter")
        self.assertTrue(
            es_monosyl_is_presatisfied(compound)
        )

    def test_es_monosyl_is_satisfied_0(self):
        compound = Compound("kind_+es_alter")
        self.assertTrue(
            es_monosyl_is_satisfied(compound)
        )

        
    def test_es_monosyl_is_presatisfied_1(self):
        compound = Compound("hund_+e_leine")
        self.assertTrue(
            es_monosyl_is_presatisfied(compound)
        )

    def test_es_monosyl_is_satisfied_1(self):
        compound = Compound("hund_+e_leine")
        self.assertTrue(
            es_monosyl_is_satisfied(compound)
        )


    def test_es_monosyl_is_presatisfied_2(self):
        compound = Compound("gesundheit_+s_system")
        self.assertTrue(
            es_monosyl_is_presatisfied(compound)
        )

    def test_es_monosyl_is_satisfied_2(self):
        compound = Compound("gesundheit_+s_system")
        self.assertFalse(
            es_monosyl_is_satisfied(compound)
        )



class TestApplicabilityCheckersZeroUmlPar(unittest.TestCase):

	# l2p:0_uml
	#
    # All nouns that constitute first constituents that attach a zero linker
    # with umlaut build the plural form with a zero ending and umlaut.

    def test_zero_uml_par_is_presatisfied_0(self):
        compound = Compound("bruder_+=_gemeinde")
        self.assertTrue(
            zero_uml_par_is_presatisfied(compound)
        )

    def test_zero_uml_par_is_satisfied_0(self):
        compound = Compound("bruder_+=_gemeinde")
        self.assertTrue(
            zero_uml_par_is_satisfied(compound)
        )

        
    def test_zero_uml_par_is_presatisfied_1(self):
        compound = Compound("hund_+e_leine")
        self.assertTrue(
            zero_uml_par_is_presatisfied(compound)
        )

    def test_zero_uml_par_is_satisfied_1(self):
        compound = Compound("hund_+e_leine")
        self.assertFalse(
            zero_uml_par_is_satisfied(compound)
        )