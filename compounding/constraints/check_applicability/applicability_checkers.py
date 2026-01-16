import pandas as pd
from typing import Optional

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

# Helper functions for plural checks

def _is_plural(
	lemma: str,
	plural_marker: Optional[str]="",
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
	return lemma_info["nom_pl"] == lemma + plural_marker


def _is_zero_plural(lemma: str) -> bool:
	# for better readability
	return _is_plural(lemma)


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
	return _is_zero_plural(compound.stems[0].morph)

def plur_0_applies(compound: Compound):
	return _has_no_linker(compound)


# p2l:decl_cl:pl:#s-0
#
# Nouns forming the plural with -s regularly attach a zero linker.

def plur_s_is_applicable(compound: Compound):
	return _is_plural(compound.stems[0].morph, "s")

def plur_s_applies(compound: Compound):
	return _has_no_linker(compound)