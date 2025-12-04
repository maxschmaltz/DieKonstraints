from compounding.constraints.gecodb_compound_parser import Compound


# 				zero_default
# The majority of compounds have a zero linker.

def zero_default_is_applicable(compound: Compound):
	# always applicable by default
	return True

def zero_default_applies(compound: Compound):
	# only one link is expected
	return compound.links[0].type == "zero"


# 				final_stressed_f
# Final-stressed (incl. one-syllable) F mostly adopt -(e)n-, a zero linker or an -s-. 
# It is possible that there is a tendency to choose by singular/plural meaning: 
# if the second constituent forces the first constituent to take a collective 
# or plural meaning, -(e)n- is more likely, otherwise mostly 
# a zero linker or -s- is chosen depending on further constraints.

def final_stressed_f_is_applicable(compound: Compound):
	pass

def final_stressed_f_applies(compound: Compound):
	pass


# 				schwa_f
# (Polysyllabic) F ending in schwa always adopt -(e)n- if the schwa is not a suffix. 
# If the schwa is a suffix of a deadjective F, -(e)n- and zero linkers are about equally possible. 
# Deverbal F with the schwa suffix mostly attach a zero linker but can attach an -(e)n- 
# when the first constituent has a plural reading.

def schwa_f_is_applicable(compound: Compound):
	pass

def schwa_f_applies(compound: Compound):
	pass