import re
import pandas as pd
from itertools import product
from typing import Optional, Literal
from germanetpy.lexunit import Lexunit

from data_utils.gecodb_compound_parser import (
    Compound,
    perform_umlaut
)
from data_utils.load_datasets import load_celex
from data_utils.germanet_search import germanet, get_n1_lexunit

celex_path = "resources/semrel_comp_corp_study-private/celex_nouns.tsv"
celex = load_celex(celex_path)



# Helper functions for property checks

# TODO: add all this checks to Constituent class in order
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
	# # to investigate the effect of the umlaut on
    # # plural effect, we disambiguate between -"er- and -er-
	# # in this version
	# if plural_marker == "er" and not adds_umlaut:
	# 	# -("")er- always adds umlaut if possible
	# 	return False
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
			# # to investigate the effect of the umlaut on
			# # plural effect, we disambiguate between -"er- and -er-
			# # in this version
			# plural_marker != "er" and	# er is allowed to have no uml
			lemma == lemma_uml	# cannot be umlauted
		):
			return False
		lemma = lemma_uml
	pl_vars = lemma_info["nom_pl"].split("/")
	return any(
		pl_var == lemma + pl_m
		for pl_var, pl_m in product(pl_vars, pl_ms)
	)


def _has_no_plural(lemma: str) -> bool:
	lemma_info = celex.loc[lemma]
	return pd.isna(lemma_info["nom_pl"])


def _is_of_gender(lemma: str, gender: Literal["m", "f", "n"]) -> bool:
	lemma_info = celex.loc[lemma]
	return gender in lemma_info["gender"]


# Helper function for derivational class checks

def _is_simplex(lemma: str) -> bool:
	lemma_info = celex.loc[lemma]
	return lemma_info["morphemic_schema"] == "N"

def _is_derived(lemma: str) -> bool:
	# for better readability
	return not _is_simplex(lemma)


def _is_prefixed(lemma: str) -> bool:
	lemma_info = celex.loc[lemma]
	# Affi(x)es: 'Ab-fahrt', 'Be-darf'
	# P(reposition)s: 'mit-Glied', 'durch-Schnitt'
	# Adverbs (B): 'fort-Schritt', 'hinter-Grund'
	return lemma_info["morphemic_schema"][0] in ["x", "P", "B"]


# Helper functions for phonetic checks

def _get_transcription(lemma: str) -> str:
	lemma_info = celex.loc[lemma]
	return lemma_info["phonetic_transcription"]


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


# Helper functions for semantic and lexical checks

def _has_hypernym(lemma: Lexunit, ids: list[str]) -> bool:
	return any(
		germanet.get_synset_by_id(id) in lemma.synset.all_hypernyms()
		for id in ids
	)

def _is_of_catergory(lemma: Lexunit, cats: str | list[str]) -> bool:
	if isinstance(cats, str):
		cats = [cats]
	# all categories present in implemented constraints
	cats2ids = {
		# we have different synsets that can identify
		# animate objects:
		# "s50990": Lebewesen, Organismus: persons, animals, insects etc.
		# "s50996": übernatürliches Lebewesen: dragons, dwarves etc.
		# "s50997": höheres Lebewesen: mammals, birds etc.
		# but since the constraint definition specifically says
		# 'animal designations', we use "s48805": Tier
		"animal": "s48805",
		# Mensch, Person, Persönlichkeit, Individuum, Menschenwesen
		"person": "s34063",
		# Stoff, Substanz, Materie
		"mass": "s47684",
		# Himmelskörper, Gestirn, Himmelsobjekt
		"astronomic_obj": "s42867",
		# Monat
		"month": "s51370"
	}
	ids = [cats2ids[cat] for cat in cats]
	return _has_hypernym(lemma, ids)



# Functions for applicability checks

# Since we are using the L2P constraints not to validate
# the prerequisites of N1 given the linker, but to
# restrict acceptable linkers, we swap the potential
# and actual applicability checkers;
# thus if an N1 does not satisfy the actual applicability
# conditions, it may not even potentially have the
# corresponding linker(s).
# We therefore rename the "_applies" function into
# "_is_satisfied" function.
# For example:
# 
# # l2p:n
#
# # All nouns that constitute first constituents 
# # that attach the -n- allomorph of the -en- linker 
# # end in schwa or in [ɐ] (unstressed -er).
#
# So if the N1 does not end in schwa or in [ɐ]
# (which is the "_applies" check!), it may not
# have -n-.
#
# Some of the L2P constraints are defined only over
# certain subclasses of nouns. For example, `l2p:s|smpx_mn`
# allows -s- specifically to simplex masc and neut nouns;
# if a masc noun is not simplex (and thus does not fulfil
# all the conditions), it does not mean it cannot attach
# -s-; it means that the acceptability of -s- remains
# undefined. Opposed to that case, some L2P constraints
# target all the nouns; if an N1 does not build the plural
# with -e-, it cannot attach -e- under no circumstances, 
# according to `l2p:e|par`. We therefore define dedicated
# "_is_presatisfied" checks that will prevent false negatives
# like described above. The "_is_presatisfied" check is
# effectively the original "_is_applicable" L2P check
# after removal of the linker condition.
#
# We remove `l2p:n` because it describes a completely
# regular phonotactic change between allomorphs,
# whereas we are aiming at predicting -n-/-en-.
#
# We remove `l2p:pl_marker|def-pl` because it is unconfirmed.


# l2p:s|smpx_mn
#
# All except for a few simplex nouns that constitute first constituents
# that attach -s- belong to a small fixed group
# of masculine and neuter nouns.

def s_smpx_is_presatisfied(compound: Compound):
	return _is_simplex(compound.constituents[0].morph)

def s_smpx_is_satisfied(compound: Compound):
	n1 = compound.constituents[0].morph
	# simplex condition already checked in applicability
	return (
		_is_of_gender(n1, "m")
		or _is_of_gender(n1, "n")
	)


# l2p:s|smpx_high_freq
#
# Many simplex nouns that constitute first constituents
# that attach -s- have a high token frequency.

def s_freq_is_presatisfied(compound: Compound):
	return _is_simplex(compound.constituents[0].morph)

def s_freq_is_satisfied(compound: Compound):
	# arbitrary measure for "high" frequency;
	# DeReKo is an enormous corpus so
	# "frequent" on its scales is measured
	# in hundreds of thousands (e.g. 'Land' has freq ~8.9M)
	return _get_frequency(compound.constituents[0].morph) > 100_000


# l2p:s|f_cmpx
#
# Almost all feminine nouns that constitute first constituents
# that attach -s- are morphologically complex.

def s_f_cmpx_is_presatisfied(compound: Compound):
	return _is_of_gender(compound.constituents[0].morph, "f")

def s_f_cmpx_is_satisfied(compound: Compound):
	return _is_derived(compound.constituents[0].morph)


# l2p:s|f_poly_syl
#
# Almost all feminine nouns that constitute first constituents
# that attach -s- are polysyllabic.

def s_f_polysyl_is_presatisfied(compound: Compound):
	return _is_of_gender(compound.constituents[0].morph, "f")

def s_f_polysyl_is_satisfied(compound: Compound):
	return _is_polysyllabic(compound.constituents[0].morph)



# l2p:en|par
#
# All nouns that constitute first constituents
# that attach -(e)n- belong are weak nouns.

def en_par_is_presatisfied(compound: Compound):
	# general restriction
	return True

def en_par_is_satisfied(compound: Compound):
	return _is_of_plural(compound.constituents[0].morph, "en")


# l2p:en|non_par_m
#
# All masculine nouns that do not build the plural form with -(e)n
# that constitute first constituents that attach -(e)n-
# are monosyllabic designations of male persons, animals,
# astronomic objects, months.

def en_non_par_m_is_presatisfied(compound: Compound):
	n1 = compound.constituents[0].morph
	return (
		_is_of_gender(n1, "m") and
		not _is_of_plural(n1, "en")
	)

def en_non_par_m_is_satisfied(compound: Compound):
	n1_lu = get_n1_lexunit(compound.lemma)
	# given a high correlation between sex and gender
	# in person designation, we assume that, since
	# only masculine nouns are covered by this constraint,
	# if they designate a person, it is a male one
	return _is_of_catergory(
		n1_lu,
		["person", "animal", "astronomic_obj", "month"]
	)



# l2p:e|par
#
# All nouns that constitute first constituents that attach -e-
# build the plural form with -e.

def e_par_is_presatisfied(compound: Compound):
	# general restriction
	return True

def e_par_is_satisfied(compound: Compound):
	return _is_of_plural(compound.constituents[0].morph, "e")


# l2p:e|#stressed_syl
#
# All nouns that constitute first constituents that attach -e- 
# have a stressed last syllable 
# or are derived of those with a stressed prefix.

def e_last_syl_is_presatisfied(compound: Compound):
	# general restriction
	return True

def e_last_syl_is_satisfied(compound: Compound):
	n1 = compound.constituents[0].morph
	return (
		_is_last_syl_stressed(n1)
		or (
			_is_prefixed(n1)
			and (n1_no_pr := _remove_prefixes(n1)[1]) in celex.index
			and _is_last_syl_stressed(n1_no_pr)
		)
	)


# l2p:e|smpx
#
# Most nouns that constitute first constituents that attach -e- are simplex.

def e_smpx_is_presatisfied(compound: Compound):
	# general restriction
	return True

def e_smpx_is_satisfied(compound: Compound):
	return _is_simplex(compound.constituents[0].morph)



# l2p:er|par
#
# All nouns that constitute first constituents that attach -(")er-
# build the plural form with -(")er.

def er_par_is_presatisfied(compound: Compound):
	# general restriction
	return True

def er_par_is_satisfied(compound: Compound):
	return (
		# to investigate the effect of the umlaut on
		# plural effect, we disambiguate between -"er- and -er-
		# in this version
		_is_of_plural(compound.constituents[0].morph, "er") or
		_is_of_plural(compound.constituents[0].morph, "er", adds_umlaut=True)
	)


# l2p:er|#stressed_syl
#
# All nouns that constitute first constituents that attach -(")er- 
# have a stressed last syllable 
# or are derived of those with a stressed prefix.

def er_last_syl_is_presatisfied(compound: Compound):
	# general restriction
	return True

def er_last_syl_is_satisfied(compound: Compound):
	n1 = compound.constituents[0].morph
	return (
		_is_last_syl_stressed(n1)
		or (
			_is_prefixed(n1)
			and (n1_no_pr := _remove_prefixes(n1)[1]) in celex.index
			and _is_last_syl_stressed(n1_no_pr)
		)
	)


# l2p:er|smpx
#
# Most nouns that constitute first constituents that attach -(")er- are simplex.

def er_smpx_is_presatisfied(compound: Compound):
	# general restriction
	return True

def er_smpx_is_satisfied(compound: Compound):
	return _is_simplex(compound.constituents[0].morph)



# l2p:e_uml
#
# All nouns that constitute first constituents that attach -"e-
# build the plural form with -e and umlaut.

def e_uml_par_is_presatisfied(compound: Compound):
	# general restriction
	return True

def e_uml_par_is_satisfied(compound: Compound):
	return _is_of_plural(compound.constituents[0].morph, "e", adds_umlaut=True)



# l2p:es|mono_syl
#
# All nouns that constitute first constituents that attach -es- are monosyllabic
# or are derived of those with a prefix.

def es_monosyl_is_presatisfied(compound: Compound):
	# general restriction
	return True

def es_monosyl_is_satisfied(compound: Compound):
	n1 = compound.constituents[0].morph
	return (
		_is_monosyllabic(n1)
		or (
			_is_prefixed(n1)
			and (n1_no_pr := _remove_prefixes(n1)[1]) in celex.index
			and _is_monosyllabic(n1_no_pr)
		)
	)



# l2p:0_uml
#
# All nouns that constitute first constituents that attach a zero linker
# with umlaut build the plural form with a zero ending and umlaut.

def zero_uml_par_is_presatisfied(compound: Compound):
	# general restriction
	return True

def zero_uml_par_is_satisfied(compound: Compound):
	return _is_of_plural(compound.constituents[0].morph, "", adds_umlaut=True)