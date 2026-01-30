import re
import pandas as pd
from ipapy import UNICODE_TO_IPA
from ipapy.ipachar import IPAChar
from itertools import product
from typing import Optional, Literal

from compounding.constraints.data_utils.gecodb_compound_parser import (
    Compound,
	Linker,
    perform_umlaut
)

# load prepared CELEX nouns
celex = pd.read_csv(
	"resources/custom/compounding/intermediate_data/celex_nouns.tsv",
	sep="\t",
	dtype=str,
	header=0,
	index_col="lemma"
)


# Helper functions for linker checks

def _has_linker(
	compound: Compound,
	linker_morph: Optional[str]="",
	adds_umlaut: Optional[bool]=False
) -> bool:
	# since we focus on N+N compounds, only one linker is always expected
	linker: Linker = compound.linkers[0]
	return (
		linker.morph == linker_morph
		and linker.adds_umlaut == adds_umlaut
	)

def _has_no_linker(compound: Compound) -> bool:
	# for better readability
	return _has_linker(compound)



# Helper functions for property checks

# TODO: add all this checks to Stem class in order
# to avoid re-accessing properties multiple times?

# Helper functions for morphological checks

def _is_of_plural(
	lemma: str,
	plural_marker: Optional[Literal["", "s", "en", "e", "er"]]="",
	adds_umlaut: Optional[bool]=False,
	dupl: Optional[bool]=False
) -> pd.Series:
	if plural_marker == "er" and not adds_umlaut:
		# -er- always adds umlaut if possible
		return False
	lemma_info = celex.loc[lemma]
	if (
		_ends_with_phon_schwa(lemma)
		and plural_marker == "en"
	):	# adjust for schwa at the end
		plural_marker = "n"
	if dupl:
		# for cases like 'Ergebnis' -> 'Ergebnisse',
		# 'Freundin' -> 'Freundinnen'
		lemma += lemma[-1]
	if adds_umlaut:
		lemma = perform_umlaut(lemma)
	pl_vars = lemma_info["nom_pl"].split("/")
	return any(
		pl_var == lemma + plural_marker
		for pl_var in pl_vars
	)

def _is_of_zero_plural(lemma: str) -> bool:
	# for better readability
	return _is_of_plural(lemma)


def _has_no_plural(lemma: str) -> bool:
	lemma_info = celex.loc[lemma]
	return pd.isna(lemma_info["nom_pl"])


def _is_of_genitive(lemma: str, genitive_marker: Literal["", "s"]) -> bool:
	# no -en genitive since all weak masculine nouns are filtered out
	lemma_info = celex.loc[lemma]
	gen_vars = lemma_info["gen_sg"].split("/")
	genitive_marker_vars = ["s", "es"] if genitive_marker == "s" else [""]
	return any(
		gen_var == lemma + genitive_marker
		for gen_var, genitive_marker in product(gen_vars, genitive_marker_vars)
	)


def _is_of_gender(lemma: str, gender: Literal["m", "f", "n"]) -> bool:
	lemma_info = celex.loc[lemma]
	return gender in lemma_info["gender"]


def _is_mixed(lemma: str) -> bool:
	return (
		(
			_is_of_gender(lemma, "m")
			or _is_of_gender(lemma, "n")
		)
		and _is_of_genitive(lemma, "s")
		and _is_of_plural(lemma, "en")
	)


# Helper function for derivational class checks

def _get_morphemic_schema(lemma: str) -> str:
	lemma_info = celex.loc[lemma]
	return lemma_info["morphemic_schema"]

def _is_simplex(lemma: str) -> bool:
	# simplex = only one morpheme; cases of conversion
	# are marked as derived in CELEX, e.g. 'Leb-en';
	# also, in some cases CELEX marks simplex nouns
	# as converted "non-derivationally",
	# e.g. 'Arbeit' `V` or 'Laut' `A`
	return len(_get_morphemic_schema(lemma)) == 1

def _is_derived(lemma: str) -> bool:
	# for better readability
	return not _is_simplex(lemma)


def _is_deverbal(lemma: str) -> bool:
	lemma_info = celex.loc[lemma]
	return "V" in lemma_info["morphemic_schema"]

def _is_deadjective(lemma: str) -> bool:
	lemma_info = celex.loc[lemma]
	return "A" in lemma_info["morphemic_schema"]


def _is_prefixed(lemma: str) -> bool:
	lemma_info = celex.loc[lemma]
	# Affi(x)es: 'Ab-fahrt', 'Be-darf'
	# P(reposition)s: 'mit-Glied', 'durch-Schnitt'
	# Adverbs (B): 'fort-Schritt', 'hinter-Grund'
	return lemma_info["morphemic_schema"][0] in ["x", "P", "B"]

def _ends_with_sfx(lemma: str, suffixes: str | list[str]) -> bool:
	if isinstance(suffixes, str):
		suffixes = [suffixes]
	lemma_info = celex.loc[lemma]
	return any(
		lemma_info["morphemic_structure"].endswith(f"-{sfx}") for sfx in suffixes
	)


# Helper functions for phonetic checks

def _get_ipa_obj(string: str) -> list[str]:
	# cannot use `IPAString` here because of
	# version incompatibilities: `ipapy` 
	# calls `MutableSequence` from `collections` instead of
	# `collections.abc` in Python 3.10+;
	# otherwise, this solution is identical and works fine
	return [UNICODE_TO_IPA[c] for c in string]

def _phone_has_property(phone: str, property: str | list[str]) -> bool:
	if isinstance(property, str):
		property = [property]
	# can be vowel/consonant,
	# voiced/voiceless, manner, place,
	# backness, height, rounded/unrounded
	ipa: IPAChar = _get_ipa_obj(phone)
	return all(
		prop in ipa[0].descriptors for prop in property
	)

def _is_vowel(phone: str) -> bool:
	# for better readability;
	# alternatively:
	# ipa = _get_ipa_obj(phone)
	# return ipa[0].is_vowel
	return _phone_has_property(phone, "vowel")

def _is_consonant(phone: str) -> bool:
	# for better readability
	# alternatively:
	# ipa = _get_ipa_obj(phone)
	# return ipa[0].is_consonant
	return _phone_has_property(phone, "consonant")

def _get_last_cons_cluster(lemma: str) -> str:
	lemma_info = celex.loc[lemma]
	ipa = _get_ipa_obj(lemma_info["phonetic_transcription"])
	is_vowels = [_phone.is_vowel for _phone in ipa]
	last_vowel_idx = is_vowels[::-1].index(True)
	if last_vowel_idx == 0:
		return ""
	last_cons_cluster = ipa[-last_vowel_idx:]
	return "".join([str(phone) for phone in last_cons_cluster])


def _get_transcription(lemma: str) -> str:
	lemma_info = celex.loc[lemma]
	return lemma_info["phonetic_transcription"]

def _ends_with_phon(lemma: str, endings: str | list[str]) -> bool:
	if isinstance(endings, str):
		endings = [endings]
	lemma_info = celex.loc[lemma]
	return any(
		_get_transcription(lemma).endswith(ending) for ending in endings
	)

def _ends_with_phon_schwa(lemma: str) -> bool:
	# for better readability
	return _ends_with_phon(lemma, "ə")

def _get_syllables(lemma: str) -> list[str]:
	phon_transcr = _get_transcription(lemma)
	syllables = phon_transcr.split(".")
	return syllables

def _has_n_syllables(lemma: str, n_syllables: int) -> bool:
	syllables = _get_syllables(lemma)
	return len(syllables) == n_syllables

def _is_monosyllabic(lemma: str) -> bool:
	# for better readability
	return _has_n_syllables(lemma, 1)

def _is_syl_stressed(lemma: str, syl_idx: int) -> bool:
	syllables = _get_syllables(lemma)
	return (
		syl_idx < len(syllables)
		and syllables[syl_idx].startswith("ˈ")
	)

def _is_trochaic(lemma: str) -> bool:
	# trochaic = Xx
	return (
		_has_n_syllables(lemma, 2)
		and _is_syl_stressed(lemma, 0)
	)

def _is_last_syl_stressed(lemma: str) -> bool:
	# for better readability
	return (
		_is_syl_stressed(lemma, -1)
		or _is_monosyllabic(lemma)
	)

# Helper for frequency check

def _get_frequency(lemma: str) -> int:
	lemma_info = celex.loc[lemma]
	return int(lemma_info["freq"])



# Functions for applicability checks

# def-0
#
# The majority of compounds have a zero linker.
# Zero linker is default for German compounds.

def def_0_is_applicable(compound: Compound):
	# applicable by default
	return True

def def_0_applies(compound: Compound):
	return _has_no_linker(compound)



# p2l:decl_cl:pl:#0-0|def-0
#
# Nouns forming the plural with a zero ending attach a zero linker regularly.

def plur_0_is_applicable(compound: Compound):
	return _is_of_zero_plural(compound.stems[0].morph)

def plur_0_applies(compound: Compound):
	return _has_no_linker(compound)



# p2l:decl_cl:pl:#s-0
#
# Nouns forming the plural with -s regularly attach a zero linker.

def plur_s_is_applicable(compound: Compound):
	return _is_of_plural(compound.stems[0].morph, "s")

def plur_s_applies(compound: Compound):
	return _has_no_linker(compound)



# p2l:decl_cl:pl:#e-0|def-0
#
# Nouns forming the plural with -e mostly have a zero linker.

def plur_e_is_applicable(compound: Compound):
	return _is_of_plural(compound.stems[0].morph, "e")

def plur_e_applies(compound: Compound):
	return _has_no_linker(compound)


# p2l:decl_cl:pl:#e-0|pl_interpr-e
#
# Nouns forming the plural with -e non-regularly attach -e- when
# the second constituent forces a plural or collective meaning of this noun.
# TODO


# p2l:decl_cl:pl:#e-0|msyl_anim-e
#
# Monosyllabic e-plural nouns designating animals non-regularly attach -e-.
# TODO



# p2l:decl_cl:pl:#er-0/er|def-0/er
#
# Nouns forming the plural with -er (with or without umlaut)
# mostly attach a zero linker or =er= in different cases.
# Another linkers can also be rarely adopted by these nouns.

def plur_er_is_applicable(compound: Compound):
	return _is_of_plural(compound.stems[0].morph, "er", adds_umlaut=True)

def plur_er_applies(compound: Compound):
	return (
		_has_no_linker(compound)
		or _has_linker(compound, linker_morph="er", adds_umlaut=True)
	)


# p2l:decl_cl:pl:#er-0/er|!pl_interpr-0
#
# Nouns forming the plural with -er (with or without umlaut) 
# attach a zero linker in majority of cases when the second 
# constituent forces a singular meaning of this noun.
# TODO


# p2l:decl_cl:pl:#er-0/er|mass-interpr-0
#
# Nouns forming the plural with -er (with or without umlaut) 
# tend (with counterexamples) to attach a zero linker 
# when the second constituent forces a mass meaning of this noun.
# TODO


# p2l:decl_cl:pl:#er-0/er|pl_interpr-er
#
# Nouns forming the plural with -er (with or without umlaut) 
# attach =er= more likely when the second constituent 
# forces a plural or collective meaning of this noun (with counterexamples), 
# in which case these nouns indicate concrete, countable entities.
# TODO


# p2l:decl_cl:pl:#er-0/er|anim-er
#
# Nouns forming the plural with -er (with or without umlaut) 
# that designate persons and animals may attach =er= 
# also with singular interpretation.
# TODO



# p2l:decl_cl:pl:#e_uml-0|def-0
#
# Nouns forming the plural with -e and umlaut 
# mostly have a zero linker.

def plur_e_uml_is_applicable(compound: Compound):
	return _is_of_plural(compound.stems[0].morph, "e", adds_umlaut=True)

def plur_e_uml_applies(compound: Compound):
	return _has_no_linker(compound)


# p2l:decl_cl:pl:#e_uml-0|pl_interpr-e_uml
#
# Nouns forming the plural with -e and umlaut non-regularly 
# attach -e- with umlaut when the second constituent 
# forces a plural or collective meaning of this noun.
# TODO



# p2l:decl_cl:pl:#0_uml-0|def-0
#
# Nouns forming the plural with a zero ending and umlaut 
# mostly have a zero linker.

def plur_0_uml_is_applicable(compound: Compound):
	return _is_of_plural(compound.stems[0].morph, "", adds_umlaut=True)

def plur_0_uml_applies(compound: Compound):
	return _has_no_linker(compound)


# p2l:decl_cl:pl:#0_uml-0|pl_interpr-0_uml
#
# Nouns forming the plural with a zero ending and umlaut 
# may non-regularly attach a zero linker with umlaut when 
# the second constituent forces a plural or collective meaning of this noun.
# TODO



# p2l:decl_cl:mixed-0/s/en|def-0/s/en
#
# Mixed masculine and neuter nouns can attach -s-, 
# a zero linker, or -(e)n-.

def mixed_mn_is_applicable(compound: Compound):
	return _is_mixed(compound.stems[0].morph)

def mixed_mn_applies(compound: Compound):
	return (
		_has_no_linker(compound)
		or _has_linker(compound, linker_morph="s")
		or _has_linker(compound, linker_morph="en")
	)


# p2l:decl_cl:mixed-0/s/en|pl_interpr-en
#
# Mixed masculine and neuter nouns can attach attach -(e)n- more likely 
# when the second constituent forces a plural or collective meaning 
# of this noun. However, there are counterexamples 
# where -(e)n- is attached even when no plural reading is possible.
# TODO



# p2l:drv:sfx:0_pl_sfx-0
#
# Derivatives with suffixes -er, -ler, -ner, -el, -sel, -chen, -lein
# that build the plural form with a zero ending
# regularly attach a zero linking element.

def sfx_pl_0_is_applicable(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		_ends_with_sfx(
			n1,
			["er", "ler", "ner", "el", "sel", "chen", "lein"]
		)
		and (
			# for cases like 'Alter'
			_has_no_plural(n1)
			or _is_of_zero_plural(n1)
		)
	)

def sfx_pl_0_applies(compound: Compound):
	return _has_no_linker(compound)



# p2l:drv:sfx:e_pl_sfx-0
#
# Nouns with suffixes -bold, -nis, -rich, -at, -al
# that build the plural form with -e regularly attach a zero linker.

def sfx_pl_e_is_applicable(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		(
			_ends_with_sfx(n1, ["bold", "rich", "at", "al"])
			and (
				# for cases like 'Personal'
				_has_no_plural(n1)
				or _is_of_plural(n1, "e")
			)
		)
		or (
			_ends_with_sfx(n1, "nis")
			and (
				# for cases like 'Unverständnis'
				_has_no_plural(n1)
				# nouns in -nis duplicate 's' in plural: '-nisse'
				or _is_of_plural(n1, "e", dupl=True)
			)
		)
	)

def sfx_pl_e_applies(compound: Compound):
	return _has_no_linker(compound)



# p2l:drv:sfx:sfx-s|def-s
#
# Nouns with suffixes -(ig)keit, -heit, -schaft, -ung, -sal, 
# -ing, -ling, -tum, -um, -ion, -(i)tät regularly attach -s-.

def sfx_s_is_applicable(compound: Compound):
	return _ends_with_sfx(
		compound.stems[0].morph,
		[
			"keit", "igkeit", "heit", "schaft", "ung", "sal",
			"ing", "ling", "tum", "um", "ion",
			# in CELEX: qualit-ät, ?, aktiv-ität, spontan-eität
			"ät", "tät", "ität", "eität"
		]
	)

def sfx_s_applies(compound: Compound):
	return _has_linker(compound, linker_morph="s")


# p2l:drv:sfx:sfx-s|#itaet$_pl_interpr-en
#
# Nouns with suffix -(i)tät prefer -en- when the second constituent 
# forces a plural or collective meaning of this noun.
# TODO



# p2l:drv:sfx:deverb_#en$-s

# -s- occurs regularly in deverbatives ending in -en.

def sfx_deverb_en_is_applicable(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		_is_deverbal(n1)
		and _ends_with_sfx(n1, "en")
	)

def sfx_deverb_en_applies(compound: Compound):
	return _has_linker(compound, linker_morph="s")



# p2l:drv:sfx:F_#in$-en
#
# Derivative feminine nouns with suffix -in always attach -en-. 
# (The suffix -in adjusts orthographically in this case and becomes an -inn.)

def sfx_F_in_en_is_applicable(compound: Compound):
	n1 = compound.stems[0].morph
	# since -in becomes -inn before -en, adjust for that
	# as in case the constraint applies, 
	# n1s like 'Lehrerinn' will be coming
	n1 = re.sub(f"{n1[-1]}{{2}}$", n1[-1], n1)
	return (
		_is_of_gender(n1, "f")
		and _ends_with_sfx(n1, "in")
	)

def sfx_F_in_en_applies(compound: Compound):
	return _has_linker(compound, linker_morph="en")



# p2l:drv:prx_deverb-s
#
# There is a strong tendency to adopt -s- after prefixed deverbatives.

def prx_deverb_is_applicable(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		_is_deverbal(n1)
		and _is_prefixed(n1)
	)

def prx_deverb_applies(compound: Compound):
	return _has_linker(compound, linker_morph="s")



# p2l:phon_fin:sibilant$-0
#
# Nouns ending in a sibilant or a consonant cluster including [s] 
# mostly adopt a zero linker.

def sibilant_fin_is_applicable(compound: Compound):
	cons_cluster = _get_last_cons_cluster(compound.stems[0].morph)
	return (
		cons_cluster
		and (
			_phone_has_property(cons_cluster[-1], "sibilant-fricative")
			or "s" in cons_cluster
		)
	)

def sibilant_fin_applies(compound: Compound):
	return _has_no_linker(compound)



# p2l:phon_fin:vow$-0
#
# Nouns ending in a full vowel always adopt a zero linker.

def vow_fin_is_applicable(compound: Compound):
	n1 = compound.stems[0].morph
	last_phone = _get_transcription(n1)[-1]
	return _is_vowel(last_phone) and not _ends_with_phon_schwa(n1)

def vow_fin_applies(compound: Compound):
	return _has_no_linker(compound)



# p2l:phon_fin:F_#stressed_phon$-0
#
# Feminine nouns endings with stressed -ei, -ie, -ur,
# also those with -ik usually attach a zero linker.

def stressed_phon_fin_is_applicable(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		_is_of_gender(n1, "f")
		and (
			(
				# stressed 'ei', 'ie', 'ur', 'ik'
				(
					# overchecking but safe
					n1.endswith("ei") and _ends_with_phon(n1, "ai")
					or n1.endswith("ie") and _ends_with_phon(n1, "i")
					or n1.endswith("ur") and _ends_with_phon(n1, "uʁ")
					# NB! the constraint applies
					# only to nouns in -ik but not to those in -ig!
					or n1.endswith("ik") and _ends_with_phon(n1, "ik")
				)
				and _is_last_syl_stressed(n1)
			)
			# unstressed 'ik'
			or _ends_with_phon(n1, "ɪk")
		)

	)

def stressed_phon_fin_applies(compound: Compound):
	return _has_no_linker(compound)



# p2l:phon_fin:F_stem_#t$-s
#
# Feminine nouns ending with a [t] often attach an -s- 
# if the [t] is part of the stem (not of a suffix).

def f_t_fin_is_applicable(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		_is_of_gender(n1, "f")
		and _ends_with_phon(n1, "t")
		and not _ends_with_sfx(
			n1,
			# all German feminine suffixes ending with [t]
			[
				"heit", "keit", "igkeit", "schaft", "falt",
				# in CELEX: qualit-ät, ?, aktiv-ität, spontan-eität
				"ät", "tät", "ität", "eität"				
			]
		)
	)

def f_t_fin_applies(compound: Compound):
	return _has_linker(compound, linker_morph="s")



# p2l:phon_fin:schwa$-en|def-en
#
# Nouns ending in schwa regularly adopt -n-.

def schwa_fin_is_applicable(compound: Compound):
	return _ends_with_phon_schwa(compound.stems[0].morph)

def schwa_fin_applies(compound: Compound):
	return _has_linker(compound, linker_morph="en")


# p2l:phon_fin:schwa$-en|deadj-0/en
#
# With deadjective feminine nouns with a schwa suffix,
# -n- and zero linkers are about equally possible.

def schwa_fin_deadj_is_applicable(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		_ends_with_phon_schwa(n1)
		and _is_deadjective(n1)
	)

def schwa_fin_deadj_applies(compound: Compound):
	return (
		_has_no_linker(compound)
		or _has_linker(compound, linker_morph="en")
	)


# p2l:phon_fin:schwa$-en|deverb-0
#
# Deverbal feminine nouns with the schwa suffix
# mostly attach a zero linker.

def schwa_fin_deverb_is_applicable(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		_ends_with_phon_schwa(n1)
		and _is_deverbal(n1)
	)

def schwa_fin_deverb_applies(compound: Compound):
	return _has_no_linker(compound)


# p2l:phon_fin:schwa$-en|deverb_pl_interpr-en
#
# Deverbal feminine nouns with the schwa suffix can attach an -n- 
# when the second constituent forces a plural or collective reading.
# TODO



# p2l:phon_fin:weak_F_cons$-0/s/en|!pl_interpr-0/s
#
# Consonant-final weak feminine nouns with a singular meaning 
# mostly adopt a zero linker or -s-.
# TODO


# p2l:phon_fin:weak_F_cons$-0/s/en|pl_interpr-en
#
# Consonant-final weak feminine attach -en- more likely (especially 
# final-stressed incl. monosyllabic ones) when the second constituent 
# forces a plural or collective meaning of this noun (with counterexamples).
# TODO



# p2l:sem:comp_type:copula-0
#
# Copulative compounds regularly attach a zero linker.
# TODO



# p2l:sem:comp_type:arg-s
#
# -s- may sometimes, with many doubtful cases, mark argumental compounds: 
# those where the second constituent still contains a high degree 
# of verbiness and the first constituent of which constitutes their argument.
# TODO



# p2l:sem:tech_term-0
#
# In technical terminology (economics, law, medicine, etc.), compounds 
# are often missing a linking element 
# (even in cases where it would be obligatory in non-technical context).
# TODO



# p2l:sem:2const_anim/pers-s
#
# Compounds with the second constituents 'Mann', 'Frau', 'Leute', 'Tochter', 
# 'Gattin', 'Witwe' can insert -s- if the compound designates a person, 
# even when the first constituent would otherwise attach a zero linker.

# def sec_const_anims_is_applicable(compound: Compound):
# 	n2 = compound.stems[1].morph.lower()
# 	return n2 in [
# 		"mann", "frau", "leute", "tochter", "gattin", "witwe"
# 	]

# def sec_const_anim_applies(compound: Compound):
# 	return _has_linker(compound, linker_morph="s")



# p2l:tend:cmpx_morph-s|def-s
#
# The acceptability of -s- irregularly grows when the first constituent 
# is morphologically complex (any form of derivation).

def cmpx_morph_is_applicable(compound: Compound):
	# universal tendency
	return True

def cmpx_morph_applies(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		(
			_is_simplex(n1)
			and not _has_linker(compound, linker_morph="s")
		)
		or (
			_is_derived(n1)
			and _has_linker(compound, linker_morph="s")
		)
	)



# p2l:tend:cmpx_phon-s|def-s
#
# The acceptability of -s- irregularly grows when the first constituent 
# is phonologically complex: non-trochaic form, words with unstressed prefixes, 
# words with stressed or semi-stressed suffixes etc.

def cmpx_phon_is_applicable(compound: Compound):
	# universal tendency
	return True

def cmpx_phon_applies(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		(
			# even though [nübling_szczepaniak_2013:78] claims
			# that the ideal is a trochee with a schwa at the end,
			# we, following [fuhrhop_kürschner_2015:572], expand
			# the definition of phonologically good words
			# with monosyllabic words and trochaic words
			# with full vowel at the end;
			# the cases of unstressed prefixes and stressed suffixes
			# do not have to be checked separately here
			# since they corrupt the trochaic pattern anyway
			_is_trochaic(n1)
			and not _has_linker(compound, linker_morph="s")
		)
		or (
			not _is_trochaic(n1)
			and _has_linker(compound, linker_morph="s")
		)
	)



# p2l:tend:sonority-!s
#
# The probability of -s- in simplices decreases with increasing sonority of the 
# final segment of the first constituent: it is more frequent after plosives, 
# infrequent after nasals and liquids, and it never occurs after a full vowel.

def sonority_is_applicable(compound: Compound):
	# even though universal tendency, none of the sources explicitly
	# mention the effect of the constraint on the occurrence of -s- after fricatives
	n1 = compound.stems[0].morph
	last_phone = _get_transcription(n1)[-1]
	return (
		_is_simplex(n1)
		and (
			_is_vowel(last_phone)
			or any (
				_phone_has_property(last_phone, prop)
				for prop in [
					"uvular", "lateral-approximant", # liquids
					"nasal", "plosive"
				]
			)
		)
	)

def sonority_applies(compound: Compound):
	last_phone = _get_transcription(compound.stems[0].morph)[-1]
	return (
		(
			(
				_is_vowel(last_phone)
				# liquids
				or (
					_phone_has_property(last_phone, ["uvular"])
					or _phone_has_property(last_phone, ["lateral-approximant"])	# [l]
				)
				# nasals
				or _phone_has_property(last_phone, ["nasal"])
			)
			and not _has_linker(compound, linker_morph="s")
		)
		or (
			_phone_has_property(last_phone, ["plosive"])
			and _has_linker(compound, linker_morph="s")
		)
	)



# p2l:tend:pl_interpr-pl_marker|def-pl_marker
#
# Linkers identical to the plural ending can be associated with plural meaning.
# TODO



# l2p:s|smpx_mn
#
# In simplexes, -s- occurs only in few masculine and neuter nouns 
# except for a few cases.

def s_smpx_is_applicable(compound: Compound):
	return (
		_has_linker(compound, linker_morph="s")
		and _is_simplex(compound.stems[0].morph)
	)

def s_smpx_applies(compound: Compound):
	n1 = compound.stems[0].morph
	# simplex condition already checked in applicability
	return (
		_is_of_gender(n1, "m")
		or _is_of_gender(n1, "n")
	)


# l2p:s|smpx_high_freq
#
# Many simplexes with an -s- are high frequent tokens.

def s_freq_is_applicable(compound: Compound):
	return (
		_has_linker(compound, linker_morph="s")
		and _is_simplex(compound.stems[0].morph)
	)

def s_freq_applies(compound: Compound):
	# arbitrary measure for "high" frequency;
	# DeReKo is an enormous corpus so
	# "frequent" on its scales is measured
	# in millions (e.g. 'Land' has freq ~8.9M)
	return _get_frequency(compound.stems[0].morph) > 500_000


# l2p:s|f
#
# -s- can occur with F only if it is a morphologically complex and/or polysyllabic F.

def s_f_cmpx_is_applicable(compound: Compound):
	return (
		_has_linker(compound, linker_morph="s")
		and _is_of_gender(compound.stems[0].morph, "f")
	)

def s_f_cmpx_applies(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		_is_derived(n1)	# at least one additional morpheme
		or not _is_monosyllabic(n1)
	)



# l2p:n
#
# Nouns ending in schwa is the only class of words that 
# can attach the allomorph -n- of the en-linker.

def n_schwa_is_applicable(compound: Compound):
	return (
		_has_linker(compound, linker_morph="en")
		and compound.linkers[0].allomorph == "n"
	)

def n_schwa_applies(compound: Compound):
	return _ends_with_phon_schwa(compound.stems[0].morph)



# l2p:en|par
#
# Only nouns forming the plural with -(e)n can attach -(e)n- as a linking element.

def en_par_is_applicable(compound: Compound):
	# general restriction
	return _has_linker(compound, linker_morph="en")

def en_par_applies(compound: Compound):
	return _is_of_plural(compound.stems[0].morph, "en")


# l2p:en|non_par_m
#
# There are a few monosyllabic masculine nouns designating male persons, 
# animals, astronomic objects, months that attach -(e)n- 
# even though they do not form the plural with -(e)n.
# TODO


# l2p:en|non_par_n_pl_interpr
#
# There are polysyllabic foreign N with final stress 
# (mostly ending with -at and -ment) that adopt -en-,
# in which case they necessarily express plurality.
# TODO



# l2p:e
#
# e-plural nouns with stressed last syllable is the only class of words 
# that can attach -e-.

def e_par_is_applicable(compound: Compound):
	return _has_linker(compound, linker_morph="e")

def e_par_applies(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		_is_of_plural(n1, "e")
		and _is_last_syl_stressed(n1)
	)



# l2p:er
#
# er-plural nouns is the only class of words 
# that can attach =er=.

def er_par_is_applicable(compound: Compound):
	return _has_linker(compound, linker_morph="er", adds_umlaut=True)

def er_par_applies(compound: Compound):
	return _is_of_plural(compound.stems[0].morph, "er", adds_umlaut=True)



# l2p:e_uml
#
# Nouns forming the plural with -e and umlaut is the only class of words 
# that can attach -e- with umlaut.

def e_uml_par_is_applicable(compound: Compound):
	return _has_linker(compound, linker_morph="e", adds_umlaut=True)

def e_uml_par_applies(compound: Compound):
	return _is_of_plural(compound.stems[0].morph, "e", adds_umlaut=True)



# l2p:es
#
# -es- occurs exclusively after a row  of one-syllable M and N 
# that form a genitive with -(e)s- (about 30-40 nouns) and is isolated. 
# These nouns can, however, also attach other linkers.
# TODO



# l2p:ens
#
# -(e)ns- only occurs after a few masculine nouns and a single neuter noun 
# not necessarily forming a genitive with -(e)ns- and is completely isolated. 
# These nouns can, however, also attach other linkers.
# TODO



# l2p:0_uml
#
# Nouns forming the plural with a zero ending and umlaut is the only class of words 
# that can attach a zero linker with umlaut.

def zero_uml_par_is_applicable(compound: Compound):
	return _has_linker(compound, linker_morph="", adds_umlaut=True)

def zero_uml_par_applies(compound: Compound):
	return _is_of_plural(compound.stems[0].morph, "", adds_umlaut=True)