from germanetpy.germanet import Germanet
from germanetpy.synset import WordCategory, Synset
from germanetpy.lexunit import Lexunit
from typing import Tuple, List, Optional

# # V19.0 (Nov 2024)
# germanet = Germanet("resources/GermaNet/V190/GN_V190_XML")

# V20.0 (Nov 2025)
germanet = Germanet("resources/GermaNet/V200/GN_V200_XML")


def get_lexunits(lemma: str) -> Optional[List[Lexunit]]:
    lemma = lemma.capitalize()
    return germanet.get_lexunits_by_orthform(lemma)


# docu:
# https://germanetpydocs.readthedocs.io/en/master/germanetpy.html#module-germanetpy.germanet
# tutorial:
# https://github.com/Blubberli/germanetpy/blob/master/germanetpy_tutorial.ipynb
def is_germanet_noun(lemma: str) -> bool:
    # synsets are sets of synonyms composed of specific
    # lexical units; we need the latter
    lexunits = get_lexunits(lemma)
    if not lexunits:
        return False
    return all(
        # 2 = noun, see docu under
        # https://germanetpydocs.readthedocs.io/en/master/germanetpy.html#germanetpy.synset.WordCategory
        lexunit.synset.word_category == WordCategory(2)
        for lexunit in lexunits
    )


def get_n1_lexunit(lemma: str) -> Synset:
    lexunits = get_lexunits(lemma)
    if len(lexunits) != 1:
        # not found in GermaNet
        # or several compound analyses, unreliable,
        # e.g. 'Kinderspiel'
        return
    comp_info = lexunits[0].compound_info
    if not comp_info:
        # not recognized as compound
        # e.g. 'Hauptautorin'
        return
    # N1 lexunits, up to three variants available
    n1_lu_ids = []
    for i in range(1, 4):
        lu_ids = getattr(comp_info, f"_mod1_LexUnitId{i}", None)
        if lu_ids:
            n1_lu_ids.extend(lu_ids)
    if len(n1_lu_ids) != 1:
        # several N1 analyses, unreliable
        # e.g. 'Landesgrenze': 'Land (Bundesland)' vs 'Land (Staat)'
        return
    return germanet.get_lexunit_by_id(n1_lu_ids[0])
