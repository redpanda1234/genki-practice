import re
import pandas as pd
import string

# Row 9 in the column name row
df = pd.read_excel("../Genki_2.xlsx", header=9)

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
    "adv.": "adv",  # adverb --- abbreviate so can filter by "verb" in
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


def clean_lesson_tag(tag_str):
    tag_strs = re.split(",|;", tag_str)

    new_tags = []
    for tag in tag_strs:
        new_str = ""
        for char in tag:
            if char in string.printable:
                new_str += char
        new_tags += [new_str.strip(" ")]
    return new_tags
