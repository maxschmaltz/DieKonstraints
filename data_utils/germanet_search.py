from germanetpy.germanet import Germanet
from germanetpy.synset import WordCategory, Synset
from typing import Tuple

# V19.0 (Nov 2024)
germanet = Germanet("resources/GermaNet/GN_V190_XML")


# docu:
# https://germanetpydocs.readthedocs.io/en/master/germanetpy.html#module-germanetpy.germanet
# tutorial:
# https://github.com/Blubberli/germanetpy/blob/master/germanetpy_tutorial.ipynb
def is_germanet_noun(lemma: str):
    lemma = lemma.capitalize()
    synsets = germanet.get_synsets_by_orthform(lemma)
    if not len(synsets):
        return False
    return all(
        # 2 = noun, see docu under
        # https://germanetpydocs.readthedocs.io/en/master/germanetpy.html#germanetpy.synset.WordCategory
        synset.word_category == WordCategory(2)
        for synset in synsets
    )


def is_synset_concrete(synset: Synset) -> bool:
    # There are only a few pre-root nodes in GermaNet
    # that can almost unambiguosly define whether a noun
    # is concrete or not:
    # * Attribut, Eigenschaft, Merkmal, Feature, Spezifikum
    # * Zustand
    # * Menge
    # * Stelle, Ort, Stätte
    # * Entität
    # All except for Entität are abstract. Entität has two
    # hyponyms: Objekt and kognitives Objekt, the latter being
    # abstract as well. Thus, only if Objekt is in the hypernyms,
    # the noun is concrete.
    return (
        germanet.get_synset_by_id("s50981")
        in synset.all_hypernyms()
    )

def get_germanet_concreteness(lemma: str) -> Tuple[bool, bool]:
    # some N1s may be concrete/abstract in their different senses:
    # 'Bad', 'Weg' etc. so we are returning a tuple of form
    # bool: a concrete sense exists
    # bool: an abstract sense exists
    lemma = lemma.capitalize()
    synsets = germanet.get_synsets_by_orthform(lemma)
    concreteness = [
        is_synset_concrete(synset)
        for synset in synsets
    ]
    return (
        True in concreteness,   # at least one synset is concrete
        False in concreteness,   # at least one synset is abstract
    )


def is_synset_mass(synset: Synset) -> bool:
    # All mass nouns are children of the
    # 'Materie/Stoff/Substanz' node.
    return (
        germanet.get_synset_by_id("s47684")
        in synset.all_hypernyms()
    )

def get_germanet_mass_senses(lemma: str) -> Tuple[bool, bool]:
    # some N1s may be mass/non-mass in their different senses:
    # 'Glas', 'Stein' etc. so we are returning a tuple of form
    # bool: a mass sense exists
    # bool: a non-mass sense exists
    lemma = lemma.capitalize()
    synsets = germanet.get_synsets_by_orthform(lemma)
    mass_senses = [
        is_synset_mass(synset)
        for synset in synsets
    ]
    return (
        True in mass_senses,   # at least one synset is mass
        False in mass_senses,   # at least one synset is non-mass
    )