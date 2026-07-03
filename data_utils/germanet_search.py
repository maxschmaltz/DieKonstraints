from germanetpy.germanet import Germanet
from germanetpy.synset import WordCategory

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