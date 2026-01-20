import pandas as pd
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

# Helper functions for morphological checks

def _is_of_plural(
	lemma: str,
	plural_marker: Optional[Literal["", "s", "en", "e", "er"]]="",
	adds_umlaut: Optional[bool]=False
) -> pd.Series:
	if plural_marker == "er" and not adds_umlaut:
		# -er- always adds umlaut if possible
		return False
	lemma_info = celex.loc[lemma]
	if (
		_ends_with_schwa(lemma)
		and plural_marker == "en"
	):	# adjust for schwa at the end
		plural_marker = "n"
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


def _is_of_genitive(lemma: str, genitive_marker: Literal["", "s"]) -> bool:
	lemma_info = celex.loc[lemma]
	gen_vars = lemma_info["gen_sg"].split("/")
	genitive_marker_vars = ["s", "es"] if genitive_marker == "s" else [""]
	return any(
		gen_var == lemma + genitive_marker
		for gen_var, genitive_marker in product(gen_vars, genitive_marker_vars)
	)


def _is_of_gender(lemma: str, gender: Literal["m", "f", "n"]) -> bool:
	lemma_info = celex.loc[lemma]
	return lemma_info["gender"] == gender


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


# Helper functions for phonetic checks

def _ends_with(lemma: str, endings: str | list[str]) -> bool:
	if isinstance(endings, str):
		endings = [endings]
	lemma_info = celex.loc[lemma]
	return any(
		lemma_info["phonetic_transcription"].endswith(ending) for ending in endings
	)

def _ends_with_schwa(lemma: str) -> bool:
	# for better readability
	return _ends_with(lemma, "@")



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
# regularly attach a zero linking element.
# TODO



# p2l:drv:sfx:!0_pl_sfx-0
#
# Nouns with suffixes -bold, -nis, -rich, -at, -al, -ik, 
# also stressed -ei, -ie, -ur usually attach a zero linker.
# TODO



# p2l:drv:sfx:sfx-s|def-s
#
# Nouns with suffixes -(ig)keit, -heit, -schaft, -ung, -sal, 
# -ing, -ling, -tum, -um, -ion, -(i)tät regularly attach -s-.
# TODO


# p2l:drv:sfx:sfx-s|#itaet$_pl_interpr-en
#
# Nouns with suffix -(i)tät prefer -en- when the second constituent 
# forces a plural or collective meaning of this noun.
# TODO



# p2l:drv:sfx:deverb_#en$-s
#
# -s- occurs regularly in deverbatives ending in -en.
# TODO



# p2l:drv:sfx:F_#in$-en
#
# Derivative feminine nouns with suffix -in always attach -en-. 
# (The suffix -in adjusts orthographically in this case and becomes an -inn.)
# TODO



# p2l:drv:prx_deverb-s
#
# There is a strong tendency to adopt -s- after prefixed deverbatives, 
# especially when the prefix is stressed.
# TODO



# p2l:phon_fin:sibilant$-0
#
# Nouns ending in a sibilant or a consonant cluster including [s] 
# mostly adopt a zero linker.
# TODO



# p2l:phon_fin:cmpx_syl$-0
#
# -s- may occur after a complex syllable boundary.
# TODO



# p2l:phon_fin:vow$-0
#
# Nouns ending in a full vowel always adopt a zero linker.
# TODO



# p2l:phon_fin:F_stem_#t$-s
#
# Feminine nouns ending with a [t] often attach an -s- 
# if the [t] is part of the stem (not of a suffix).
# TODO



# p2l:phon_fin:schwa$-en|def-en
#
# Nouns ending in schwa regularly adopt -n-.
# TODO


# p2l:phon_fin:schwa$-en|deadj-0/en
#
# With deadjective feminine nouns with a schwa suffix, -n- 
# and zero linkers are about equally possible.
# TODO


# p2l:phon_fin:schwa$-en|deverb-0
#
# Deverbal feminine nouns with the schwa suffix mostly attach a zero linker.
# TODO


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
# TODO



# p2l:tend:cmpx_morph-s|def-s
#
# The acceptability of -s- irregularly grows when the first constituent 
# is morphologically complex (any form of derivation).
# TODO



# p2l:tend:cmpx_phon-s|def-s
#
# The acceptability of -s- irregularly grows when the first constituent 
# is phonologically complex: non-trochaic form, words with unstressed prefixes, 
# words with stressed or semi-stressed suffixes etc.
# TODO



# p2l:tend:sonority-!s
#
# The probability of -s- decreases with increasing sonority of the 
# final segment of the first constituent: it is more frequent after plosives, 
# infrequent after nasals and liquids, and it never occurs after a full vowel.
# TODO



# p2l:tend:pl_interpr-pl_marker|def-pl_marker
#
# Linkers identical to the plural ending can be associated with plural meaning.
# TODO



# l2p:s|smpx_mn
#
# In simplexes, -s- occurs only in few masculine and neuter nouns 
# except for a few cases.
# TODO


# l2p:s|smpx_high_freq
#
# Many simplexes with an -s- are high frequent tokens.
# TODO


# l2p:s|f
#
# -s- can occur with F only if it is a morphological complex and/or polysyllabic F.
# TODO



# l2p:n
#
# Nouns ending in schwa is the only class of words that 
# can attach the allomorph -n- of the en-linker.
# TODO



# l2p:en|par
#
# Only nouns forming the plural with -(e)n can attach -(e)n- as a linking element.
# TODO


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
# TODO



# l2p:er
#
# er-plural nouns (these are few words, mostly N and some M, 
# mostly simplices and never loanwords) is the only class of words 
# that can attach =er=.
# TODO



# l2p:e_uml
#
# Nouns forming the plural with -e and umlaut is the only class of words 
# that can attach -e- with umlaut.
# TODO



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
# TODO