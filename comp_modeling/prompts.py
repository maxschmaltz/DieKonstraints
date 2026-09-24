PREDICT_LINKER_PROMPT = """\
You are a German native speaker and you help me \
with my homework. My task is to join two nouns into \
a compound noun existing in German. My textbook provides \
the following examples:

EXAMPLE 1
Nouns: 'Freund' and 'Kreis'
Variants: 'Freundekreis', 'Freundeskreis', 'Freundkreis'
Correct answer: 'Freundeskreis'

EXAMPLE 2
Nouns: 'Herz' and 'Bedürfnis'
Variants: 'Herzbedürfnis', 'Herzenbedürfnis', 'Herzensbedürfnis'
Correct answer: 'Herzensbedürfnis'

Below is the real task I have. Please help me and pick
the correct answer from the given Variants. There is always
only one correct answer in the Variants so make sure that you
find it exclusively among them. Only return the correct answer
without any tags, punctuation, or any other marks. Don't think
about the answer, return directly what you believe is the correct option.

REAL TASK
Nouns: '{n1}' and '{n2}'
Variants: {variants}
Correct answer: 
"""