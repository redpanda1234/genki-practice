import re
import json
import js2py
import genanki
import requests

from multiprocessing import Pool
from bs4 import BeautifulSoup
from tqdm import tqdm
from copy import deepcopy

from constants import *
from genki_ingest import *

from pitch_accent_utils import *


def clean_word(word):
    return re.sub("[a-zA-Z ＋]*", "", re.sub("（[^>]+）", "", word))


def filter_non_kana(some_str):
    new_str = ""
    for char in some_str:
        if char in kana_str:
            new_str += char
    return new_str


print("Adding npm furigana package thing...")
furi = js2py.require("furigana").fit
print("Done!")


def get_furigana(kanji_word, reading):
    return_me = ""
    try:
        return_me = furi(kanji_word, reading)
    except:
        print(f"this reading is fucked: {reading}. Kanji was {kanji_word}")
        assert False
    try:
        assert return_me is not None
    except AssertionError:
        print(f"this reading made the js break: {reading}. Kanji was {kanji_word}")
    return return_me


def test_word(k_word, reading):
    furigana = get_furigana(k_word, reading)
    pitch_str = get_pitch(k_word, furigana)
    return furigana, pitch_str


def main():
    pre_dfrows = [row for (_, row) in df.iterrows()]

    # Some words are stored in the genki excel file with multiple
    # kanji. It's actually just two: kotae and hayaku.
    dfrows = []
    for row in pre_dfrows:
        if not pd.isnull(row["kanji"]):
            newrow = deepcopy(row)
            kanjis = row["kanji"].split("/")
            for kanji in kanjis:
                newrow["kanji"] = kanji
                dfrows += [newrow]
        else:
            dfrows += [row]

    for row in tqdm(dfrows):
        row_tags = clean_lesson_tag(row["lesson"])
        if not pd.isnull(row["kanji"]):
            kanji = clean_word(row["kanji"])
            word = clean_word(row["word"])
            # REMOVE THIS
            if "、" in word:
                print(f"these are fucked: {kanji}, {word}")
                continue

            if kanji[0] in shitty_tildes and word[0] in shitty_tildes:
                kanji = kanji[1:]
                word = word[1:]
            if kanji[-1] in shitty_tildes and word[-1] in shitty_tildes:
                kanji = kanji[0:-1]
                word = word[0:-1]
            # assert "～" == "〜"

            # Treat the cases where there are multiple valid pronunciations
            words = word.split("/")
            furiganas = []
            pitches = []
            for word in words:
                try:
                    assert set(word) <= set(kana_str)
                except AssertionError:
                    print(
                        f"what the fuck is happening in word {word} for kanji {kanji}"
                    )
                    assert False

                furigana = get_furigana(kanji, word)
                # pitch_str = get_pitch(kanji, furigana)

                furiganas += [furigana]
                # pitches += [pitch_str]

            try:
                f_str = "\n\n".join(furiganas)
            except TypeError:
                print(word, kanji)
            # print(f_str)
            # p_str = "\n\n".join(pitches)

            # pitch_note = genanki.Note(
            #     model=genki_pitch_model,  # in constants.py
            #     fields=[
            #         row["kanji"],
            #         f_str,
            #         row["english"],
            #         row["pos"],
            #         p_str,
            #     ],
            #     tags=row_tags,
            # )
        # else:
        #     # lmao this is kind of dumb
        #     pitch_str = get_pitch(row["word"], row["word"])
        #     pitch_note = genanki.Note(
        #         model=genki_pitch_model,
        #         fields=[
        #             row["word"],
        #             row["word"],
        #             row["english"],
        #             row["pos"],
        #             pitch_str,
        #         ],
        #         tags=row_tags,
        #     )

    #     # pitch deck in constants.py
    #     genki_pitch_deck.add_note(pitch_note)

    # genanki.Package(genki_pitch_deck).write_to_file(
    #     "~/files/genki-practice/anki-data/test-test-anki.apkg"
    # )


if __name__ == "__main__":
    main()


# [\w ]*[0-9]*\%|[█▏▎▍▌▊▋▉▉]*[\w ]*|[ ]*[0-9/ ]*\[[0-9,:< \.a-z/]*\]\0
