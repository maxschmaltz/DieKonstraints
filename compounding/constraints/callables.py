from compounding.constraints.gecodb_compound_parser import Compound


# 				zero_default
# The majority of compounds have a zero linker.

def zero_default_is_applicable(compound: Compound):
	# always applicable by default
	return True

def zero_default_applies(compound: Compound):
	# only one link is expected
	return compound.links[0].type == "zero"


# 				one_syl_f
# Final-stressed (incl. one-syllable) F mostly adopt -(e)n-, a zero linker or an -s-. 
# It is possible that there is a tendency to choose by singular/plural meaning: 
# if the second constituent forces the first constituent to take a collective 
# or plural meaning, -(e)n- is more likely, otherwise mostly 
# a zero linker or -s- is chosen depending on further constraints.

def one_syl_f_is_applicable(compound: Compound):
	pass

def one_syl_f_applies(compound: Compound):
	pass