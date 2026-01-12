from compounding.constraints.gecodb_compound_parser import Compound


# 				zero_default
# The majority of compounds have a zero linker.

def zero_default_is_applicable(compound: Compound):
	# applicable by default
	return True

def zero_default_applies(compound: Compound):
	# here and further: since we focus on N+N
	# compounds, only one link is always expected
	return compound.links[0].type == "zero"
