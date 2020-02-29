# For working with the genki csv
import pandas as pd

# Automatic verb conjugation, sort of
from japaneseverbconjugator.src import JapaneseVerbFormGenerator
from japaneseverbconjugator.src.constants.EnumeratedTypes import (
    VerbClass,
    Tense,
    Polarity,
)

jvfg = JapaneseVerbFormGenerator.JapaneseVerbFormGenerator()

# ================================================================== #
# The provided macros are too verbose for me
#
# Requires: verb, verb_class, tense, polarity
plain_form = jvfg.generate_plain_form

# Requires: verb, verb_class
te_form = jvfg.generate_te_form

# たい form. Requires: verb, verb_class, formality, polarity
volitional_form = jvfg.generate_volitional_form
# ------------------------------------------------------------------ #


xl_file = pd.ExcelFile("Genki_2.xlsx")
dfs = {sheet_name: xl_file.parse(sheet_name) for sheet_name in xl_file.sheet_names}

# There's only one dataframe in the dictionary
df = dfs["単語さくいん（第2版）"]

# Dictionary for converting between parts of speech and the way genki
# refers to them
parts_of_speech = {
    "i": "い-adj.",
    "n": "n.",
    "na": "な-adj.",
    "u": "u-v.",
    "ru": "ru-v.",
    "ir": "irr-v.",
    "adv": "adv.",
    "part": "part.",
    "pre": "pre.",
    "suf": "suf.",
    "exp": "exp.",
}

colnames = {"word": "単語", "kanji": "漢字表記", "pos": "品詞", "english": "英訳", "lesson": "課数"}
