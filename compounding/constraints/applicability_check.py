from compounding.constraints.data_utils.gecodb_compound_parser import Compound, Linker


	# # here and further: since we focus on N+N
	# # compounds, only one linker is always expected
	# linker: Linker = compound.links[0]
	# return linker.allomorph == "" and not linker.adds_umlaut


# 				def-0
# The majority of compounds have a zero linker.
# Zero linker is default for German compounds.

def zero_default_is_applicable(compound: Compound):
	# applicable by default
	return True

def zero_default_applies(compound: Compound):
	pass
