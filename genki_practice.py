# For working with the genki csv
import pandas as pd
import nouns

# Pick random nouns, verbs, etc.
from random import choice as pick

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
polite_form = jvfg.generate_polite_form

# Requires: verb, verb_class, tense, polarity
plain_form = jvfg.generate_plain_form

# Requires: verb, verb_class
te_form = jvfg.generate_te_form

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

# Define an easy-access list of verbs
verb_df = filter_by(df, "pos", "verb")
verb_list = [entry for entry in verb_df["english"]]


def write_nouns():
    """
    write nouns to a text file so that we can do stuff with them
    """
    text_file = open("Nouns.txt", "w")
    n_df = filter_by(df, "pos", "noun")
    noun_string = ""
    for noun in n_df["english"].values:
        noun_string += f'"{noun}",\n'
    text_file.write(noun_string)
    text_file.close


def verb_to_verbing(verb):
    """
    convert an english verb to "ing" form, or at least try to.
    """
    if verb[0:3] == "to ":
        verb = verb[3:]
    # print(verb)
    index = verb.find(" ", 0, len(verb))

    if index == -1:
        if verb[index] == "e":
            return verb[:index] + "ing"
        else:
            return verb + "ing"
    else:
        if verb[index] == "e":
            verb = verb[0:index] + verb[index + 1 :]

    return verb[0:index] + "ing" + verb[index:]


def verb_class(en_verb):
    verb = df[[en_verb == entry for entry in df["english"]]]
    verb_class = verb["pos"].values[0]
    if verb_class == "ru-verb":
        return VerbClass.ICHIDAN
    elif verb_class == "u-verb":
        return VerbClass.GODAN
    elif verb_class == "irr-verb":
        return VerbClass.IRREGULAR
    else:
        assert False  # Haha what


def j_verb_class(j_verb):
    """
    same as above but the input is japanese
    """
    verb = df[[j_verb == entry for entry in df["word"]]]
    if len(verb) == 0:
        verb = df[[j_verb == entry for entry in df["kanji"]]]

    verb_class = verb["pos"].values[0]

    if verb_class == "ru-verb":
        return VerbClass.ICHIDAN
    elif verb_class == "u-verb":
        return VerbClass.GODAN
    elif verb_class == "irr-verb":
        return VerbClass.IRREGULAR
    else:
        assert False  # Haha what


def japanese(english):
    """
    return the japanese word corresponding to the `english` entry in
    our dataframe. Must be the exact wording given in the textbook.
    """
    row = df[[english == entry for entry in df["english"]]]
    return row["word"].values[0]


def english(japanese):
    """
    return the japanese word corresponding to the `english` entry in
    our dataframe. Must be the exact wording given in the textbook.
    """
    row = df[[japanese == entry for entry in df["word"]]]
    return row["word"].values[0]


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
    Qualifying nouns with verbs and adjectives (see: L9, pg. 213-214)
    """
    # The method by which we'll indicate who is the subject of our
    # sentence. These crrespond to the 4 examples given on page 214.
    options = ["place", "frequency", "verb", "time"]
    option = pick(options)

    # Pick the verb
    verb = "it"
    while ("(something)" in verb) or (
        verb[0:2] == "it"
    ):  # don't want verbs like "はじまる"
        verb = pick(verb_list)

    ja_verb = japanese(verb)
    vclass = verb_class(verb)

    if option == "place":
        en_verb = verb_to_verbing(verb)  # make it into the "ing" form
        ja_te_verb = te_form(ja_verb, vclass)

        english_prompt = f"The person who is [{en_verb}] over there"
        response = f"あそこで{ja_te_verb}いる人"

    elif option == "frequency":
        freq = pick(nouns.frequency)  # Get a frequency word
        jfreq = japanese(freq)  # Convert it to japanese too

        en_verb = verb[3:]  # remove the leading "to "

        english_prompt = f"People who [{en_verb}] {freq}"
        response = f"{jfreq}{ja_verb}人"

    elif option == "verb":
        (polarity, eng_pol) = pick(
            [(Polarity.POSITIVE, ""), (Polarity.NEGATIVE, "NOT")]
        )

        en_verb = verb[3:]  # remove the leading "to "
        ja_ta_verb = plain_form(ja_verb, vclass, Tense.NONPAST, polarity)
        english_prompt = f"People who do {eng_pol} [{en_verb}]"
        response = f"{ja_ta_verb}人"

    else:
        time = pick(nouns.times_past)
        jtime = japanese(time)

        en_verb = verb[3:]  # remove the leading "to "
        ja_ta_verb = plain_form(ja_verb, vclass, Tense.PAST, Polarity.POSITIVE)

        english_prompt = f"A friend who [{en_verb} (PAST)] {time}"
        response = f"{jtime}{ja_ta_verb}友だち"

    # elif option == "time":
    try:
        user_input = input("translate " + english_prompt + "\n")
    except UnicodeDecodeError:
        pass

    print(f"Sample response is: {response}\n")

    return  # response


def single_short_form(verb, eng_pol, eng_tense, ja_verb, vclass, polarity, tense):
    en_verb = verb
    if eng_pol == "NEGATIVE":
        en_verb = en_verb[0:3] + "NOT " + en_verb[3:]

    if eng_tense == "PAST":
        en_verb = en_verb[0:3] + "(have) " + en_verb[3:]

    english_prompt = f'Short form of "{en_verb}":'

    response = plain_form(ja_verb, vclass, tense, polarity)

    return_me = None

    try:
        user_input = input(english_prompt + "\n")
        print(f"you said {user_input}")
        if user_input != response:
            return_me = (verb, eng_pol, eng_tense, ja_verb, vclass, polarity, tense)

    except UnicodeDecodeError:
        pass

    print(f"Correct conjugation is: {response}\n")

    return return_me


def random_short_form():
    """
    This one picks a random short form and then runs single_short_form
    to quiz on it

    We keep these functions separate so that we can do a primitive
    review feature in short_form_practice by feeding wrong ones back
    into single_short_form later
    """
    polarity, eng_pol = pick(
        [(Polarity.NEGATIVE, "NEGATIVE"), (Polarity.POSITIVE, "AFFIRMATIVE")]
    )

    tense, eng_tense = pick([(Tense.PAST, "PAST"), (Tense.NONPAST, "NONPAST")])

    # Pick the verb
    verb = "it"
    while ("(something)" in verb) or (
        verb[0:2] == "it"
    ):  # don't want verbs like "はじまる"
        verb = pick(verb_list)

    ja_verb = japanese(verb)
    vclass = verb_class(verb)

    return single_short_form(verb, eng_pol, eng_tense, ja_verb, vclass, polarity, tense)


def short_form_practice(n):
    wrong = []
    for _ in range(n):
        response = random_short_form()
        if response is not None:
            wrong += [response]

    while wrong:
        print(f"{len(wrong)} verbs to review.")
        review = pick([1, 2, 3])
        if review == 1:
            forgotten_verb = wrong[0]
            wrong = wrong[1:]
            response = single_short_form(*forgotten_verb)
            if response is not None:
                wrong += [response]
        else:
            response = random_short_form()
            if response is not None:
                wrong += [response]

    return


def single_ongoing_negative():
    # verb = pick(verb_list)

    (ntype, verb, did, have_already_done, did_not_do, have_not_done) = pick(
        [
            (
                nouns.do_able,
                "する",
                "did",
                "have already done",
                "did not do",
                "have not done",
            ),
            (
                nouns.eat_able,
                "たべる",
                "ate",
                "have already eaten",
                "didn't eat",
                "have not eaten",
            ),
            (
                nouns.drink_able,
                "のむ",
                "drank",
                "have already drunk",
                "did not drink",
                "haven't drunk",
            ),
            (
                nouns.write_able,
                "かく",
                "wrote",
                "already wrote",
                "did not write",
                "haven't written",
            ),
            (
                nouns.buy_able,
                "かう",
                "bought",
                "already bought",
                "did not buy",
                "haven't bought",
            ),
            (
                nouns.places_absolute,
                "いく",
                "went",
                "already went",
                "didn't go",
                "haven't gone",
            ),
        ]
    )

    noun = pick(ntype)

    # Ok I know this is garbage and I should be handling cases more
    # intelligently but idk lay off ok
    tense = pick([1, 2, 3, 4])

    if tense == 1:
        time = pick(nouns.times_past)
        english_prompt = f"I {did} the {noun} {time}."
        vclass = j_verb_class(verb)
        jverb = polite_form(verb, vclass, Tense.PAST, Polarity.POSITIVE)
        response = f"わたしは{japanese(time)}{japanese(noun)}を{jverb}"

    elif tense == 2:

        english_prompt = f"I {have_already_done} the {noun}."
        vclass = j_verb_class(verb)
        jverb = polite_form(verb, vclass, Tense.PAST, Polarity.POSITIVE)
        response = f"わたしはもう{japanese(noun)}を{jverb}"

    if tense == 3:
        time = pick(nouns.times_past)
        english_prompt = f"I {did_not_do} the {noun} {time}."
        vclass = j_verb_class(verb)
        jverb = polite_form(verb, vclass, Tense.PAST, Polarity.NEGATIVE)
        response = f"わたしは{japanese(time)}{japanese(noun)}を{jverb}"

    elif tense == 4:
        english_prompt = f"I {have_not_done} the {noun} yet."
        vclass = j_verb_class(verb)
        jverb = te_form(verb, vclass)
        response = f"わたしはまだ{japanese(noun)}を{jverb}いません"

    try:
        user_input = input(english_prompt + "\n")
        # print(f"you said {user_input}")
        if user_input != response:
            print(f"{response} is the expected answer\n")
            return
        else:
            print("correct\n")
    except UnicodeDecodeError:
        print(f"{response} is the expected answer.\n")
        pass


def comparison_practice():

    pass


def plan_practice():
    (ntype, j_verb, j_part, en_verb) = pick(
        [
            (nouns.do_able, "する", "を", "to do"),
            (nouns.eat_able, "たべる", "を", "to eat"),
            (nouns.see_able, "みる", "を", "to see"),
            (nouns.read_able, "よむ", "を", "to read"),
            (nouns.drink_able, "のむ", "を", "to drink"),
            (nouns.write_able, "かく", "を", "to write"),
            (nouns.buy_able, "かう", "を", "to buy"),
            (nouns.places_absolute, "いく", "に", "to go"),
        ]
    )

    en_noun = pick(ntype)
    j_noun = japanese(en_noun)

    vclass = j_verb_class(j_verb)

    past, polarity, en_tense, j_tense = pick(
        [
            (True, Polarity.POSITIVE, "I was planning", "つもりでした",),
            (True, Polarity.NEGATIVE, "I was not planning", "つもりでした",),
            (False, Polarity.POSITIVE, "I plan", "つもりです",),
            (False, Polarity.NEGATIVE, "I do not plan", "つもりです",),
        ]
    )

    if past:
        # If somehting _was_ our plan before, it could have been for
        # any time.
        en_time = pick(nouns.times_past + nouns.times_future + nouns.times_absolute)

    elif pick([True, True, False]):  # Give it some shitty odds
        en_time = pick(nouns.times_future)

    else:
        en_time = pick(nouns.times_absolute)

    time_part = ""
    if en_time in nouns.times_absolute:
        time_part = "に"

    j_time = japanese(en_time)

    j_verb = plain_form(j_verb, vclass, Tense.NONPAST, polarity)

    english_prompt = f'Translate "{en_tense} {en_verb} {en_noun} {en_time}"'
    response = f"わたしは{j_time}{time_part}{j_noun}{j_part}{j_verb}{j_tense}"

    try:
        user_input = input(english_prompt + "\n")
        # print(f"you said {user_input}")
        if user_input != response:
            print(f"{response} is the expected answer\n")
            return
        else:
            print("correct\n")
    except UnicodeDecodeError:
        print(f"{response} is the expected answer.\n")
        pass


def become_practice():
    pass


def tai_practice():
    (ntype, j_verb, en_verb) = pick(
        [
            (nouns.do_able, "する", "to do"),
            (nouns.study_able, "勉強する", "to study"),
            (nouns.become_able, "なる", "to become"),
            (nouns.animals, "飼う", "to own"),
            (nouns.eat_able, "食べる", "to eat"),
            (nouns.see_able, "見る", "to see"),
            (nouns.read_able, "読む", "to read"),
            (nouns.drink_able, "飲む", "to drink"),
            (nouns.write_able, "書く", "to write"),
            (nouns.buy_able, "買う", "to buy"),
            # (nouns.places_absolute, "行く", "to go"),
        ]
    )

    en_noun = pick(ntype)
    j_noun = japanese(en_noun)

    vclass = j_verb_class(j_verb)

    tai_suffix, en_prefix = pick(
        [
            ("たいです", "[I] want"),
            ("たくないです", "[I] do not want"),
            ("たかった", "[I] wanted"),
            ("たくなかった", "[I] didn't want"),
            ("たがっています", "[Mary] seems to want"),
            ("たがっていました", "[Mary] seems to have wanted"),
        ]
    )

    # if past:
    #     # If somehting _was_ our plan before, it could have been for
    #     # any time.
    #     en_time = pick(nouns.times_past + nouns.times_future + nouns.times_absolute)
    # else:
    #     en_time = pick(nouns.times_future + nouns.times_absolute)
    # j_time = japanese(en_time)

    j_verb = polite_form(j_verb, vclass, Tense.NONPAST, Polarity.POSITIVE)

    # Trim off the 「ます」at the end
    j_verb = j_verb[0:-2]

    english_prompt = f'Translate "{en_prefix} {en_verb} {en_noun}"'
    response = f"{j_noun}を{j_verb}{tai_suffix}"

    try:
        user_input = input(english_prompt + "\n")
        # print(f"you said {user_input}")
        if user_input != response:
            print(f"{response} is the expected answer\n")
            return
        else:
            print("correct\n")
    except UnicodeDecodeError:
        print(f"{response} is the expected answer.\n")
        pass


def n_desu_practice():
    pass


def youd_better_practice():
    pass


def obligation_practice():

    particle = "を"

    (ntype, j_verb, en_verb) = pick(
        [
            (nouns.do_able, "する", "to do"),
            (nouns.study_able, "勉強する", "to study"),
            (nouns.become_able, "なる", "to become"),
            # (nouns.animals, "飼う", "to own"),
            (nouns.eat_able, "食べる", "to eat"),
            (nouns.see_able, "見る", "to see"),
            (nouns.read_able, "読む", "to read"),
            (nouns.drink_able, "飲む", "to drink"),
            (nouns.write_able, "書く", "to write"),
            (nouns.buy_able, "買う", "to buy"),
            (nouns.places_absolute, "行く", "to go"),
        ]
    )

    if j_verb == "行く":
        particle = "に"

    en_noun = pick(ntype)
    j_noun = japanese(en_noun)

    vclass = j_verb_class(j_verb)

    in_the_past = pick([True, False])
    do_n_desu = pick([True, False])

    n_desu = ""
    en_time = ""

    if in_the_past:
        en_time = pick(nouns.times_past)
        j_time = japanese(en_time)
        en_prefix = "[I] had"
        j_suffixes = [
            "ければいけませんでした",
            "きゃいけませんでした",
            "くちゃいけませんでした",
        ]
        if do_n_desu:
            n_desu = "なんでした"

    else:
        en_time = pick(nouns.times_future)
        j_time = japanese(en_time)
        en_prefix = "[I] have"
        j_suffixes = [
            "ければいけません",
            "きゃいけません",
            "くちゃいけません",
        ]

        if do_n_desu:
            n_desu = "なんです"

    j_verb = plain_form(j_verb, vclass, Tense.NONPAST, Polarity.NEGATIVE)
    j_verb = j_verb[0:-1]  # Trim off the 「い」at the end

    english_prompt = f'Translate "{en_prefix} {en_verb} {en_noun} {en_time}"'
    possible_responses = [
        f"{j_time}{j_noun}{particle}{j_verb}{j_suffix}" for j_suffix in j_suffixes
    ]

    try:
        user_input = input(english_prompt + "\n")
        # print(f"you said {user_input}")
        if user_input not in possible_responses:
            print("Any of the following would have been accepted:\n")
            for response in possible_responses:
                print(response)
            return
        else:
            print("correct\n")
    except UnicodeDecodeError:
        print("Any of the following would have been accepted:\n")
        for response in possible_responses:
            print(response)
        pass
