from compounding.constraints.gecodb_compound_parser import Compound


# zero_default
# The majority of compounds have a zero linker.
def zero_default_is_applicable(
	compound: Compound
):
	# always applicable by default
	return True

def zero_default_applies(
	compound: Compound
):
	# only one link is expected
	return compound.links[0].type == "concatenation"