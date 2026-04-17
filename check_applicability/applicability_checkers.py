import re
import pandas as pd
from ipapy import UNICODE_TO_IPA
from ipapy.ipachar import IPAChar
from itertools import product
from typing import Optional, Literal

from data_utils.gecodb_compound_parser import (
    Compound,
	Linker,
    perform_umlaut
)


celex_path = "resources/developed/celex_nouns.tsv"
gecodb_path = "resources/developed/gecodb_v06.tsv"

# load prepared CELEX nouns and GeCoDB
celex = pd.read_csv(
	celex_path,
	sep="\t",
	dtype=str,
	header=0,
	index_col="lemma"
)

# load GeCoDB
gecodb_v06 = pd.read_csv(
	gecodb_path,
	sep="\t",
	dtype=str,
	header=0,
	index_col="comp_gecodb"
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

def _remove_prefixes(lemma: str) -> str:
	lemma_info = celex.loc[lemma]
	s_idx, _ = re.search(
		"[NAVR]",
		lemma_info["morphemic_schema"]
	).span()
	morphemes = lemma_info["morphemic_structure"].split("-")
	prefixes = "".join(morphemes[:s_idx])
	lemma_no_prefix = re.sub(rf"^{prefixes}", "", lemma)
	return prefixes, lemma_no_prefix

def _is_of_plural(
	lemma: str,
	plural_marker: Optional[Literal["", "s", "en", "e", "er"]]="",
	adds_umlaut: Optional[bool]=False,
	dupl: Optional[bool]=False
) -> pd.Series:
	if plural_marker == "er" and not adds_umlaut:
		# -("")er- always adds umlaut if possible
		return False
	lemma_info = celex.loc[lemma]
	if _has_no_plural(lemma):
		return False	# has no plural
	pl_ms = (
		# adopt for cases with schwa, er, el etc.
		["n", "en"] if plural_marker == "en"
		else [plural_marker]
	)
	if dupl:
		# for cases like 'Ergebnis' -> 'Ergebnisse',
		# 'Freundin' -> 'Freundinnen'
		lemma += lemma[-1]
	if adds_umlaut:
		# during result analysis, we identified some cases in which
		# "umlautable" prefixes were erroneously
		# umlauted ('Vorbild', 'Abstand')
		prefixes, lemma_no_prefix = _remove_prefixes(lemma)
		lemma_no_prefix_uml = perform_umlaut(lemma_no_prefix)
		lemma_uml = prefixes + lemma_no_prefix_uml
		# this is to avoid cases like
		# Stern, _+=e_ ---> True
		if (
			plural_marker != "er"	# er is allowed to have no uml
			and lemma == lemma_uml	# cannot be umlauted
		):
			return False
		lemma = lemma_uml
	pl_vars = lemma_info["nom_pl"].split("/")
	return any(
		pl_var == lemma + pl_m
		for pl_var, pl_m in product(pl_vars, pl_ms)
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

def _is_simplex(lemma: str) -> bool:
	lemma_info = celex.loc[lemma]
	return lemma_info["morphemic_schema"] == "N"

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

def _is_polysyllabic(lemma: str) -> bool:
	# for better readability
	return not _is_monosyllabic(lemma)

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
# First constituents that are constituted
# by simplex masculine or neuter nouns
# that build the plural form with a zero ending
# and simplex or complex feminine nouns
# that build the plural form with a zero ending
# attach a zero linker almost regularly.

def plur_0_is_applicable(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		(
			(
				# smpx m/n
				not _is_of_gender(n1, "f")
				and _is_simplex(n1)
			)
			# smpx/cmpx f
			or _is_of_gender(n1, "f")
		)
		# 0-pl
		and _is_of_zero_plural(n1)
	)

def plur_0_applies(compound: Compound):
	return _has_no_linker(compound)



# p2l:decl_cl:pl:#s-0
#
# First constituents that are constituted by nouns that build
# the plural form with -s attach a zero linker regularly.

def plur_s_is_applicable(compound: Compound):
	return _is_of_plural(compound.stems[0].morph, "s")

def plur_s_applies(compound: Compound):
	return _has_no_linker(compound)



# p2l:decl_cl:pl:#e-0|def-0
#
# First constituents that are constituted by nouns that build
# the plural form with -e mostly have a zero linker.

def plur_e_is_applicable(compound: Compound):
	return _is_of_plural(compound.stems[0].morph, "e")

def plur_e_applies(compound: Compound):
	return _has_no_linker(compound)


# p2l:decl_cl:pl:#e-0|pl_interpr-e
#
# First constituents that are constituted by nouns that build
# the plural form with -e attach -e- irregularly in compounds
# in which the second constituent forces
# a plural meaning of the given first constituent.
# TODO


# p2l:decl_cl:pl:#e-0|msyl_anim-e
#
# First constituents that are constituted by
# monosyllabic animal designations that build
# the plural form with -e attach -e- irregularly.
# TODO



# p2l:decl_cl:pl:#er-0/er|def-0/er
#
# First constituents that are constituted by nouns that build
# the plural form with -(")er
# mostly attach a zero linker or -(")er-.

def plur_er_is_applicable(compound: Compound):
	return _is_of_plural(compound.stems[0].morph, "er", adds_umlaut=True)

def plur_er_applies(compound: Compound):
	return (
		_has_no_linker(compound)
		or _has_linker(compound, linker_morph="er", adds_umlaut=True)
	)


# p2l:decl_cl:pl:#er-0/er|!pl_interpr-0
#
# First constituents that are constituted by nouns that build
# the plural form with -(")er
# attach a zero linker in majority of compounds
# in which the second constituent forces
# a singular meaning of the given first constituent.
# TODO


# p2l:decl_cl:pl:#er-0/er|mass-interpr-0
#
# First constituents that are constituted by nouns that build
# the plural form with -(")er
# tend to attach a zero linker in compounds
# in which the second constituent forces
# a mass meaning of the given first constituent.
# TODO


# p2l:decl_cl:pl:#er-0/er|pl_interpr-er
#
# First constituents that are constituted by nouns that build
# the plural form with -(")er
# attach -(")er- more likely in compounds
# in which the second constituent forces
# a plural meaning of the given first constituent.
# TODO


# p2l:decl_cl:pl:#er-0/er|anim-er
#
# First constituents that are constituted by
# person and animal designations that build
# the plural form with -(")er
# may attach -(")er- regardless of the
# singular/pluralinterpretation of
# the given first constituent within the compound.
# TODO



# p2l:decl_cl:pl:#e_uml-0|def-0
#
# First constituents that are constituted by nouns that build
# the plural form with -e and umlaut mostly have a zero linker.

def plur_e_uml_is_applicable(compound: Compound):
	return _is_of_plural(compound.stems[0].morph, "e", adds_umlaut=True)

def plur_e_uml_applies(compound: Compound):
	return _has_no_linker(compound)


# p2l:decl_cl:pl:#e_uml-0|pl_interpr-e_uml
#
# First constituents that are constituted by nouns that build
# the plural form with -e and umlaut attach -"e- irregularly in compounds
# in which the second constituent forces
# a plural meaning of the given first constituent.
# TODO



# p2l:decl_cl:pl:#0_uml-0|def-0
#
# First constituents that are constituted by nouns that build
# the plural form with a zero ending and umlaut mostly have a zero linker.

def plur_0_uml_is_applicable(compound: Compound):
	return _is_of_plural(compound.stems[0].morph, "", adds_umlaut=True)

def plur_0_uml_applies(compound: Compound):
	return _has_no_linker(compound)


# p2l:decl_cl:pl:#0_uml-0|pl_interpr-0_uml
#
# First constituents that are constituted by nouns that build
# the plural form with a zero ending and umlaut attach
# a zero linker with umlaut irregularly in compounds
# in which the second constituent forces
# a plural meaning of the given first constituent.
# TODO



# p2l:decl_cl:mixed-0/s/en|def-0/s/en
#
# First constituents that are constituted by
# mixed masculine and neuter nouns
# almost always attach -s-, a zero linker, or -(e)n-.

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
# First constituents that are constituted by
# mixed masculine and neuter nouns attach -(e)n-more likely in compounds
# in which the second constituent forces
# a plural meaning of the given first constituent.
# TODO



# p2l:drv:sfx:0_pl_sfx-0
#
# First constituents that are constituted by derived nouns with suffixes
# -er, -ler, -ner, -el, -sel, -chen, -lein that build the plural form
# with a zero ending attach a zero linking element regularly.

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
# First constituents that are constituted by derived nouns with suffixes
# -bold, -nis, -rich, -at, -al that build
# the plural form with -e attach a zero linker regularly.

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



# p2l:drv:deverb_schwa$-0|def-0
#
# First constituents that are constituted by deverbal feminine nouns
# with a schwa suffix mostly attach a zero linker.

def schwa_fin_deverb_is_applicable(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		_ends_with_phon_schwa(n1)
		and _is_deverbal(n1)
	)

def schwa_fin_deverb_applies(compound: Compound):
	return _has_no_linker(compound)


# p2l:drv:deverb_schwa$-0|pl_interpr-en
#
# First constituents that are constituted by deverbal feminine nouns
# with a schwa suffix tend to attach -n- in compoundsin which the second
# constituent forces a plural reading of the given first constituent.
# TODO



# p2l:drv:deadj_schwa$-0/en
#
# First constituents that are constituted by deadjectival feminine nouns
# with a schwa suffix almost always attach -n- or a zero linker.
# Each of the two linkers is preferred in about the same number of cases.

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



# p2l:drv:sfx:sfx-s|def-s
#
# First constituents that are constituted by derived nouns with suffixes
# -(ig)keit, -heit, -schaft, -ung, -sal, -ing, -ling, -tum, -um, -ion,
# also -ität and its allomorphs attach -s- regularly.

def sfx_s_is_applicable(compound: Compound):
	return _ends_with_sfx(
		compound.stems[0].morph,
		[
			"keit", "igkeit", "heit", "schaft", "ung", "sal",
			"ing", "ling", "tum", "um", "ion",
			# in CELEX: absorb-tion (added manually), design-ation
			"tion", "ation",
			# in CELEX: qualit-ät, ?, aktiv-ität, spontan-eität, plast-izität
			"ät", "tät", "ität", "eität", "izität"
		]
	)

def sfx_s_applies(compound: Compound):
	return _has_linker(compound, linker_morph="s")


# p2l:drv:sfx:sfx-s|#itaet$_pl_interpr-en
#
# First constituents that are constituted by derived nouns with suffix
# -ität and its allomorphs prefer -en- in compounds in which the second
# constituent forces a plural meaning of the given first constituent.
# TODO



# p2l:drv:sfx:deverb_#en$-s

# First constituents that are constituted by deverbal nouns
# that end in suffix -en attach -s- regularly.

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
# First constituents that are constituted by derived feminine nouns
# with suffix -in always attach -en-.
# (The suffix -in adjusts orthographically in this case and becomes -inn.)

def sfx_F_in_en_is_applicable(compound: Compound):
	n1 = compound.stems[0].morph
	# since -in becomes -inn before -en, adjust for that
	# as in case the constraint applies, 
	# n1s like 'Lehrerinn' will be coming
	n1 = re.sub(f"inn$", "in", n1)
	try:
		return (
			_is_of_gender(n1, "f")
			and _ends_with_sfx(n1, "in")
		)
	except KeyError:
		return False	# for cases like Sinn - sin

def sfx_F_in_en_applies(compound: Compound):
	return _has_linker(compound, linker_morph="en")



# p2l:drv:prx_deverb-s
#
# First constituents that are constituted by prefixed deverbal nouns
# exhibit a strong tendency to attach -s-.

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
# First constituents that are constituted by nouns that endin a sibilant
# or in a consonant cluster including [s] mostly adopt a zero linker.

def sibilant_fin_is_applicable(compound: Compound):
	cons_cluster = _get_last_cons_cluster(compound.stems[0].morph)
	return (
		bool(cons_cluster)
		and (
			_phone_has_property(cons_cluster[-1], "sibilant-fricative")
			or "s" in cons_cluster
		)
	)

def sibilant_fin_applies(compound: Compound):
	return _has_no_linker(compound)



# p2l:phon_fin:vow$-0
#
# First constituents that are constituted by nouns that end
# in a full vowel always adopt a zero linker.

def vow_fin_is_applicable(compound: Compound):
	n1 = compound.stems[0].morph
	phon_transcription = _get_transcription(n1)
	last_phone = phon_transcription[-1]
	last_bo_phone = phon_transcription[-2]
	return (
		_is_vowel(last_phone)
		# avoid diphthongs
		and not _is_vowel(last_bo_phone)
		and not _ends_with_phon_schwa(n1)
	)

def vow_fin_applies(compound: Compound):
	return _has_no_linker(compound)



# p2l:phon_fin:F_#stressed_phon$-0
#
# First constituents that are constituted by feminine nouns that end 
# with stressed -ei, -ie, -ur, also stressed or unstressed -ik
# usually attach a zero linker.

def stressed_phon_fin_is_applicable(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		_is_of_gender(n1, "f")
		and (
			(
				# stressed 'ei', 'ie', 'ur', 'ik'
				(
					# overchecking but safe
					(n1.endswith("ei") and _ends_with_phon(n1, "ai"))
					or (n1.endswith("ie") and _ends_with_phon(n1, "i"))
					or (n1.endswith("ur") and _ends_with_phon(n1, "uʁ"))
					# NB! the constraint applies
					# only to nouns in -ik but not to those in -ig!
					or (n1.endswith("ik") and _ends_with_phon(n1, "ik"))
				)
				and _is_last_syl_stressed(n1)
			)
			# unstressed 'ik'
			or (n1.endswith("ik") and _ends_with_phon(n1, "ɪk"))
		)

	)

def stressed_phon_fin_applies(compound: Compound):
	return _has_no_linker(compound)



# p2l:phon_fin:F_stem_#t$-s
#
# First constituents that are constituted by polysyllabic feminine nouns
# that end with [t] often attach -s- if the [t] is not part of a suffix
# -(ig)keit, -heit, -schaft, or -ität or its allomorphs.

def f_t_fin_is_applicable(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		_is_of_gender(n1, "f")
		and _is_polysyllabic(n1)
		and _ends_with_phon(n1, "t")
		and not _ends_with_sfx(
			n1,
			[
				"heit", "keit", "igkeit", "schaft",
				# in CELEX: qualit-ät, ?, aktiv-ität, spontan-eität
				"ät", "tät", "ität", "eität"				
			]
		)
	)

def f_t_fin_applies(compound: Compound):
	return _has_linker(compound, linker_morph="s")



# p2l:phon_fin:schwa$-en|def-en
#
# First constituents that are constituted by nouns 
# that end in schwa mostly adopt -n-.

def schwa_fin_is_applicable(compound: Compound):
	return _ends_with_phon_schwa(compound.stems[0].morph)

def schwa_fin_applies(compound: Compound):
	return _has_linker(compound, linker_morph="en")


# p2l:phon_fin:schwa$-en|f-en
#
# First constituents that are constituted by feminine nouns 
# that end in schwa adopt -n- regularly.

def schwa_fin_f_is_applicable(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		_is_of_gender(n1, "f")
		and _ends_with_phon_schwa(n1)
	)

def schwa_fin_f_applies(compound: Compound):
	return _has_linker(compound, linker_morph="en")



# p2l:phon_fin:weak_F_cons$-0/s/en|!pl_interpr-0/s
#
# First constituents that are constituted by
# consonant-final weak feminine nouns mostly adopt a zero linker or -s- 
# in compounds in which the second constituent forces
# a singular meaning of the given first constituent.
# TODO


# p2l:phon_fin:weak_F_cons$-0/s/en|pl_interpr-en
#
# First constituents that are constituted by
# consonant-final weak feminine nouns --- especially final-stressed
# incl. monosyllabic ones --- attach -en- more likely in compounds
# in which the second constituent forces
# a plural meaning of the given first constituent.
# TODO



# p2l:sem:comp_type:copula-0
#
# Copulative compounds insert a zero linker regularly.
# By copulative compounds are understood compounds in which
# the two constituents do not exhibit a clear modifier-head relation.
# TODO



# p2l:sem:comp_type:arg-s
#
# Argumental compounds are sometimes marked by -s-.
# By argumental compounds are understood compounds in which
# the second constituent still contains a high degree of verbiness
# and the first constituent of which constitutes their argument.
# The second constituent is such compounds is usually
# an agent designation, an -ung formation etc.
# TODO



# p2l:sem:tech_term-0
#
# Compounds belonging to technical terminology (economics, law,
# medicine, etc.) are often missing an explicit linking element
# (even in cases where it would be obligatory in a non-technical context).
# TODO



# p2l:sem:2const_anim/pers-s
#
# Compounds with second constituents 'Mann', 'Frau', 'Leute',
# 'Tochter', 'Gattin', 'Witwe' tend to insert -s-
# if the compound designates a person
# (even if the first constituent would otherwise attach a zero linker).

# def sec_const_anims_is_applicable(compound: Compound):
# 	n2 = compound.stems[1].morph.lower()
# 	return n2 in [
# 		"mann", "frau", "leute", "tochter", "gattin", "witwe"
# 	]

# def sec_const_anim_applies(compound: Compound):
# 	return _has_linker(compound, linker_morph="s")



# p2l:tend:cmpx_morph-s|def-s
#
# The probability of -s- grows irregularly with the
# morphological complexity of the first constituent
# (any form of derivation).

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
# The probability of -s- grows irregularly with the
# phonological complexity of the first constituent.
# By phonologically complex words are understood
# words with polysyllable non-trochaic form,
# words with unstressed prefixes,
# words with stressed or semi-stressed suffixes etc.

def cmpx_phon_is_applicable(compound: Compound):
	# universal tendency
	return True

def cmpx_phon_applies(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		(
			# even though [nuebling_szczepaniak_2013:78] claims
			# that the ideal is a trochee with a schwa at the end,
			# we, following [fuhrhop_kuerschner_2015:572], expand
			# the definition of phonologically good words
			# with monosyllabic words and trochaic words
			# with full vowel at the end;
			# the cases of unstressed prefixes and stressed suffixes
			# do not have to be checked separately here
			# since they corrupt the trochaic pattern anyway
			(
				_is_monosyllabic(n1)
				or _is_trochaic(n1)
			)
			and not _has_linker(compound, linker_morph="s")
		)
		or (
			not _is_trochaic(n1)
			and _has_linker(compound, linker_morph="s")
		)
	)



# p2l:tend:sonority-!s
#
# The probability of -s- in compounds with simplex first constituents
# tends to decrease with the increasing sonority of the final segment
# of the first constituent. -s- is thus more frequent after plosives,
# infrequent after nasals and liquids,
# and it never occurs after a full vowel.

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



# l2p:s|smpx_mn
#
# All except for a few simplex nouns that constitute first constituents
# that attach -s- belong to a small fixed group
# of masculine and neuter nouns.

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
# Many simplex nouns that constitute first constituents
# that attach -s- have a high token frequency.

def s_freq_is_applicable(compound: Compound):
	return (
		_has_linker(compound, linker_morph="s")
		and _is_simplex(compound.stems[0].morph)
	)

def s_freq_applies(compound: Compound):
	# arbitrary measure for "high" frequency;
	# DeReKo is an enormous corpus so
	# "frequent" on its scales is measured
	# in hundreds of thousands (e.g. 'Land' has freq ~8.9M)
	return _get_frequency(compound.stems[0].morph) > 100_000


# l2p:s|f_cmpx
#
# Almost all feminine nouns that constitute first constituents
# that attach -s- are morphologically complex.

def s_f_cmpx_is_applicable(compound: Compound):
	return (
		_has_linker(compound, linker_morph="s")
		and _is_of_gender(compound.stems[0].morph, "f")
	)

def s_f_cmpx_applies(compound: Compound):
	return _is_derived(compound.stems[0].morph)


# l2p:s|f_poly_syl
#
# Almost all feminine nouns that constitute first constituents
# that attach -s- are polysyllabic.

def s_f_polysyl_is_applicable(compound: Compound):
	return (
		_has_linker(compound, linker_morph="s")
		and _is_of_gender(compound.stems[0].morph, "f")
	)

def s_f_polysyl_applies(compound: Compound):
	return _is_polysyllabic(compound.stems[0].morph)



# l2p:n
#
# All nouns that constitute first constituents
# that attach the -n- allomorph of the -en- linker end in schwa.

def n_schwa_is_applicable(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		_has_linker(compound, linker_morph="en")
		and compound.linkers[0].allomorph == "n"
		# this is to exclude the special case for nouns
		# ending in a stressed [i:] (-ie) or in a stressed [e:] (-ee)
		# such as such as 'Melodie', 'Kategorie, 'Idee', 'Kaffee';
		# in cases like 'melodie_+n_folge' or 'idee_+n_austausch',
		# even though orphographically they have -n-, it is phonologically
		# an -en-: Melod[I:] vs Melod[Ien]folge, Id[E:] vs Id[Een]austausch
		# which becomes -n- just to avoid a confusing vocal cluster such
		# as *Melodieenfolge, *Ideeenaustausch
		and not (
			(
				# overchecking but safe
				(n1.endswith("ee") and _ends_with_phon(n1, "e"))
				or (n1.endswith("ie") and _ends_with_phon(n1, "i"))
			)
			and _is_last_syl_stressed(n1)
		)
	)

def n_schwa_applies(compound: Compound):
	return _ends_with_phon_schwa(compound.stems[0].morph)



# l2p:en|par
#
# All nouns that constitute first constituents
# that attach -(e)n- belong are weak nouns.

def en_par_is_applicable(compound: Compound):
	# general restriction
	return _has_linker(compound, linker_morph="en")

def en_par_applies(compound: Compound):
	return _is_of_plural(compound.stems[0].morph, "en")


# l2p:en|non_par_m
#
# All masculine nouns that do not build the plural form with -(e)n
# that constitute first constituents that attach -(e)n-
# are monosyllabic designations of male persons, animals,
# astronomic objects, months.
# TODO


# l2p:en|non_par_n_pl_interpr
#
# All neuter nouns that do not build the plural form with -(e)n
# that constitute first constituents that attach -(e)n-
# are polysyllabic foreign nouns that have a stressed final syllable
# (and mostly end in -at and -ment) that exhibit
# a plural meaning within the compound.
# TODO



# l2p:e|par
#
# All nouns that constitute first constituents that attach -e-
# build the plural form with -e.

def e_par_is_applicable(compound: Compound):
	return _has_linker(compound, linker_morph="e")

def e_par_applies(compound: Compound):
	return _is_of_plural(compound.stems[0].morph, "e")


# l2p:e|#stressed_syl
#
# All nouns that constitute first constituents that attach -e-
# have a stressed last syllable.

def e_last_syl_is_applicable(compound: Compound):
	return _has_linker(compound, linker_morph="e")

def e_last_syl_applies(compound: Compound):
	return _is_last_syl_stressed(compound.stems[0].morph)


# l2p:e|smpx
#
# Most nouns that constitute first constituents that attach -e- are simplex.

def e_smpx_is_applicable(compound: Compound):
	return _has_linker(compound, linker_morph="e")

def e_smpx_applies(compound: Compound):
	return _is_simplex(compound.stems[0].morph)


# l2p:e|!loan:
#
# All nouns that constitute first constituents that attach -e-
# are native (none are loanwords).
# TODO



# l2p:er|par
#
# All nouns that constitute first constituents that attach -(")er-
# build the plural form with -(")er.

def er_par_is_applicable(compound: Compound):
	return _has_linker(compound, linker_morph="er", adds_umlaut=True)

def er_par_applies(compound: Compound):
	return _is_of_plural(compound.stems[0].morph, "er", adds_umlaut=True)


# l2p:er|#stressed_syl
#
# All nouns that constitute first constituents that attach -(")er-
# have a stressed last syllable.

def er_last_syl_is_applicable(compound: Compound):
	return _has_linker(compound, linker_morph="er", adds_umlaut=True)

def er_last_syl_applies(compound: Compound):
	return _is_last_syl_stressed(compound.stems[0].morph)


# l2p:er|smpx
#
# Most nouns that constitute first constituents that attach -(")er- are simplex.

def er_smpx_is_applicable(compound: Compound):
	return _has_linker(compound, linker_morph="er", adds_umlaut=True)

def er_smpx_applies(compound: Compound):
	return _is_simplex(compound.stems[0].morph)


# l2p:er|!loan
#
# All nouns that constitute first constituents that attach -(")er-
# are native (none are loanwords).
# TODO



# l2p:e_uml
#
# All nouns that constitute first constituents that attach -"e-
# build the plural form with -e and umlaut.

def e_uml_par_is_applicable(compound: Compound):
	return _has_linker(compound, linker_morph="e", adds_umlaut=True)

def e_uml_par_applies(compound: Compound):
	return _is_of_plural(compound.stems[0].morph, "e", adds_umlaut=True)



# l2p:es|isol
#
# All nouns that constitute first constituents that attach -es- belong
# to a fixed row of masculine and neuter nouns and
# build the genitive form with -(e)s-. -es- is thus isolated.
# TODO


# l2p:es|mono_syl
#
# All nouns that constitute first constituents that attach -es- are monosyllabic.

def es_monosyl_is_applicable(compound: Compound):
	return _has_linker(compound, linker_morph="es")

def es_monosyl_applies(compound: Compound):
	return _is_monosyllabic(compound.stems[0].morph)



# l2p:ens
#
# All nouns that constitute first constituents that attach -(e)ns-
# belong to a fixed group of a few masculine nouns and a single neuter noun
# and have different genitive endings. -(e)ns- is thus isolated.
# TODO



# l2p:0_uml
#
# All nouns that constitute first constituents that attach a zero linker
# with umlaut build the plural form with a zero ending and umlaut.

def zero_uml_par_is_applicable(compound: Compound):
	return _has_linker(compound, linker_morph="", adds_umlaut=True)

def zero_uml_par_applies(compound: Compound):
	return _is_of_plural(compound.stems[0].morph, "", adds_umlaut=True)



# p2l:tend:pl_interpr-pl_marker|def-pl_marker
#
# Linkers that are identical to the plural ending
# of the first constituent in a given compound
# tend to be associated with
# a plural meaning of this first constituent within the compound.
# TODO



# Functions for applicability checks for correction suggestions

# p2l:drv:sfx:e_pl_sfx-0
#
# First constituents that are constituted by derived nouns with suffixes 
# -bold, -nis, -rich, -al that build 
# the plural form with -e attach a zero linker regularly.

def sfx_pl_e_is_applicable_corr(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		(
			_ends_with_sfx(n1, ["bold", "rich", "al"])
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

def sfx_pl_e_applies_corr(compound: Compound):
	return _has_no_linker(compound)



# p2l:drv:sfx:deverb_#en$-s

# First constituents that are constituted by deverbal nouns that end
# in suffix -en [mostly] attach -s-. 
# [Zero linker variants with a significantly lower frequency may occur.]

def sfx_deverb_en_is_applicable_corr(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		_is_deverbal(n1)
		and _ends_with_sfx(n1, "en")
	)

def sfx_deverb_en_applies_corr(compound: Compound):
	return (
		_has_linker(compound, linker_morph="s")
		or (
			_has_no_linker(compound)
			and (
				(
					s_var := compound.stems[0].morph
					+ "_+s_" + compound.stems[1].morph
				)
				in gecodb_v06.index
			) and (
				(
					int(gecodb_v06.loc[s_var, "comp_freq"])
					/ int(gecodb_v06.loc[compound.gecodb, "comp_freq"])
				) >= 3	# at least 3 times less frequent
			)
		)
	)



# p2l:phon_fin:vow$-0
#
# First constituents that are constituted by nouns that end
# in a full vowel adopt a zero linker [regularly 
# unless this noun is a loanword that ends 
# with a stressed long [i] (-ie) or a stressed long [e] (-ee)].

def vow_fin_is_applicable_corr(compound: Compound):
	n1 = compound.stems[0].morph
	phon_transcription = _get_transcription(n1)
	last_phone = phon_transcription[-1]
	last_bo_phone = phon_transcription[-2]
	return (
		_is_vowel(last_phone)
		# avoid diphthongs
		and not _is_vowel(last_bo_phone)
		and not _ends_with_phon_schwa(n1)
		and not (
			last_phone == "i"					# i
			and _is_consonant(last_bo_phone)	# Ci
			and _is_last_syl_stressed(n1)		# 'X*Ci
			and n1.endswith("ie")
		)
	 and not (
			last_phone == "e"					# e
			and _is_consonant(last_bo_phone)	# Ce
			and _is_last_syl_stressed(n1)		# 'X*Ce
			and n1.endswith("ee")
		)
	)

def vow_fin_applies_corr(compound: Compound):
	return _has_no_linker(compound)



# p2l:phon_fin:schwa$-en
#
# [Almost all] first constituents that are constituted 
# by [simplex] feminine nouns that end in schwa adopt -n-.

def schwa_fin_f_is_applicable_corr(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		_is_simplex(n1)
		and _is_of_gender(n1, "f")
		and _ends_with_phon_schwa(n1)
	)

def schwa_fin_f_applies_corr(compound: Compound):
	return _has_linker(compound, linker_morph="en")



# l2p:n
#
# All nouns that constitute first constituents 
# that attach the -n- allomorph of the -en- linker 
# end in schwa [or in [ɐ] (unstressed -er)].

def n_schwa_is_applicable_corr(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		_has_linker(compound, linker_morph="en")
		and compound.linkers[0].allomorph == "n"
		# this is to exclude the special case for nouns
		# ending in a stressed [i:] (-ie) or in a stressed [e:] (-ee)
		# such as such as 'Melodie', 'Kategorie, 'Idee', 'Kaffee';
		# in cases like 'melodie_+n_folge' or 'idee_+n_austausch',
		# even though orphographically they have -n-, it is phonologically
		# an -en-: Melod[I:] vs Melod[Ien]folge, Id[E:] vs Id[Een]austausch
		# which becomes -n- just to avoid a confusing vocal cluster such
		# as *Melodieenfolge, *Ideeenaustausch
		and not (
			(
				# overchecking but safe
				(n1.endswith("ee") and _ends_with_phon(n1, "e"))
				or (n1.endswith("ie") and _ends_with_phon(n1, "i"))
			)
			and _is_last_syl_stressed(n1)
		)
	)

def n_schwa_applies_corr(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		_ends_with_phon_schwa(n1)
		or (
			n1.endswith("er")
			# [ɐ] is realized as [əʁ] in CELEX-nouns
			and _ends_with_phon(n1, "əʁ")
		)
	)



# l2p:e|#stressed_syl
#
# All nouns that constitute first constituents that attach -e- 
# have a stressed last syllable 
# [or are derived of those with a stressed prefix].

def e_last_syl_is_applicable_corr(compound: Compound):
	return _has_linker(compound, linker_morph="e")

def e_last_syl_applies_corr(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		_is_last_syl_stressed(n1)
		or (
			_is_prefixed(n1)
			and (n1_no_pr := _remove_prefixes(n1)[1]) in celex.index
			and _is_last_syl_stressed(n1_no_pr)
		)
	)



# l2p:er|#stressed_syl
#
# All nouns that constitute first constituents that attach -(")er- 
# have a stressed last syllable 
# [or are derived of those with a stressed prefix].

def er_last_syl_is_applicable_corr(compound: Compound):
	return _has_linker(compound, linker_morph="er", adds_umlaut=True)

def er_last_syl_applies_corr(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		_is_last_syl_stressed(n1)
		or (
			_is_prefixed(n1)
			and (n1_no_pr := _remove_prefixes(n1)[1]) in celex.index
			and _is_last_syl_stressed(n1_no_pr)
		)
	)



# l2p:es|mono_syl
#
# All nouns that constitute first constituents that attach -es- are monosyllabic
# [or are derived of those with a prefix].

def es_monosyl_is_applicable_corr(compound: Compound):
	return _has_linker(compound, linker_morph="es")

def es_monosyl_applies_corr(compound: Compound):
	n1 = compound.stems[0].morph
	return (
		_is_monosyllabic(n1)
		or (
			_is_prefixed(n1)
			and (n1_no_pr := _remove_prefixes(n1)[1]) in celex.index
			and _is_monosyllabic(n1_no_pr)
		)
	)