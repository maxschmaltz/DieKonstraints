# Even though AWK files are in general much more efficient than Python scripts for text processing tasks,
# we choose to implement this data preparation script in Python for several reasons:
# 1) Complexity of preprocessing: many files are involved simultaneously,
#    which would make the AWK code quite convoluted and hard to maintain.
# 2) Readability and maintainability: Python code is often more readable and easier to maintain than AWK code,
#    especially for complex tasks.
# 3) Personal competence in Python, hence, faster development cycle and more reliable code.


def main():

    # In preparing the CELEX data for our compounding constraints, we need to extract the following data
    # for all the non-compound nouns:
    # 1) Lemma.
    # 2) Morphological information: gender, GenSg form, NomPL form; the latter two are needed to determine
    #    the inflectional class of the noun. Used in morphological constraints.
    # 3) Morphemic structure: to identify prefixes and suffixes. Used in derivational constraints.
    # 4) Derivational information: to identify base nouns of derived nouns to be able to identify
    #    deverbal/deadjective/etc. nouns. Used in derivational constraints.
    # 4) Phonological information: to identify the final segment(s) of the noun. Used in phonological constraints.
    # 5) Syllabic structure: to identify monosyllabic vs. polysyllabic nouns as well as phonological quality of the noun.
    #    Used in phonological constraints.
    # 6) Frequency information.
    # Semantic and lexical properties are not contained in the CELEX data, so we do not extract them here.


    # To extract all the nencessary data, we need to parse the following files (see more about the files in
    # resources/Celex/german/gml/README):
    # 1) gml.cd: 'German Morphology, Lemmas'. This file contains lemmas, 
    #    



    # last but one column


    # We start by parsing gml.cd. TODO
    pass



if __name__ == "__main__":
    main()