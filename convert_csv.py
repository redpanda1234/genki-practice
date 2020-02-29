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


# Row 9 in the column name row
df = pd.read_excel("Genki_2.xlsx", header=9)

# The columns have names written in japanese. I'm not going to mutate
# the csv in any way so we'll just rename the columns of the dataframe
# as we instantiate it.
#
# "pos" is for "part of speech"
c = {"単語": "word", "漢字表記": "kanji", "品詞": "pos", "英訳": "english", "課数": "lesson"}
df.rename(columns=c, inplace=True)


# Replace the "parts of speech" entries with easier labels.
#
# Yes, they're longer (for the most part), but it's just easier to
# read in-place so whatever.
parts_of_speech = {
    "n.": "noun",  # noun
    "い-adj.": "i-adj",  # i adjective
    "な-adj.": "na-adj",  # na adjective
    "u-v.": "u-verb",  # u verb
    "ru-v.": "ru-verb",  # ru verb
    "irr-v.": "irr-verb",  # irregular verb
    "adv.": "adverb",  # adverb
    "part.": "particle",  # particle
    "pre.": "pre-nom",  # pre-nominal expression, e.g. 「その___」
    "suf.": "nf-suffix",  # (noun-forming) suffix, e.g. 「___円」or「___か月」
    "exp.": "expression",  # expression
}

# Replace the columns
df["pos"].replace(parts_of_speech, inplace=True)


def filter_by(df, col, val):
    """
    df: the genki csv dataframe
    col: the column we want to filter in
    val: the value we want to filter for

    Example:
        filter_by(df, "lesson", "L15")

    We have to do this because pandas built-in filtering scheme
    doesn't allow us to filter by things like `val in df[col]`, so we
    can't do things like `"L11" in df[col]` because the columns are
    formatted like "会L11-II" or something.
    """
    # If we passed in a list of values to filter by, we check for
    # where _any_ of them are valid
    if type(val) == list:
        return df[
            [any([val_entry in df_entry for val_entry in val]) for df_entry in df[col]]
        ]

    # Create a simple bool array to index into the dataframe with
    return df[[val in entry for entry in df[col]]]


# Get vocab for lessons 3-12. We have to get vocab for lessons 1 and 2
# separately because the "in" part messes up by including things from
# L11, L12, L13, ... because they all contain L1.
#
# I guess I should have just hard-coded this from the beginning but
# w/e.
our_lessons = [f"L{i}" for i in range(3, 13)]
df = filter_by(df, "lesson", our_lessons)
l1df = df[[("会L1" == entry) or ("L1," in entry) for entry in df["lesson"]]]
l2df = df[[("会L2" == entry) or ("L2," in entry) for entry in df["lesson"]]]
df = pd.concat([df, l1df, l2df])


# ================================================================== #
#                                                                    #
#                        Ok now the real shit                        #
#                                                                    #
# ================================================================== #
#                                                                    #
#                      (i.e. practice functions)                     #
#                                                                    #
# ------------------------------------------------------------------ #


def qualify_noun():
    """
    Qualifying nouns with verbs and adjectives (see: L9, pg. 213)
    """

    return
