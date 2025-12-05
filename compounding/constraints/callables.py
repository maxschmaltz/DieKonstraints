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


# 				copula
# Copulative compounds regularly attach a zero linker.

def copula_is_applicable(compound: Compound):
	pass

def copula_applies(compound: Compound):
	pass


# 				final_full_v
# Nouns ending on a full vowel always adopt a zero linker.

def final_full_v_is_applicable(compound: Compound):
	pass

def final_full_v_applies(compound: Compound):
	pass



# 				tech_term
# In technical terminology (economics, law, medicine, etc.), compounds 
# are often missing a linking element (even in cases where 
# it would be obligatory in non-technical context).

def tech_term_is_applicable(compound: Compound):
	pass

def tech_term_applies(compound: Compound):
	pass


# 				null_plural
# Derivatives forming a plural with a zero ending -- 
# especially with suffixes -er, -ler, -ner, -el, -sel, -chen, -lein -- 
# attach a zero linking element regularly. Those with suffix -en 
# also attach a zero linker unless they are a deverbative, 
# in which case they mostly attach -s-.

def null_plural_is_applicable(compound: Compound):
	pass

def null_plural_applies(compound: Compound):
	pass


# 				second_const_pers_design
# Compounds with the second constituents 'Mann', 'Frau', 'Leute',
# 'Tochter', 'Gattin', 'Witwe' can insert -s- or -es-, 
# if the compound designates a person, even when the first constituent 
# would otherwise attach a zero linker.

def second_const_pers_design_is_applicable(compound: Compound):
	pass

def second_const_pers_design_applies(compound: Compound):
	pass