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
    return word.replace("（〜を）", "").replace("〜", "")


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
    return furi(kanji_word, reading)


def test_word(k_word, reading):
    furigana = get_furigana(k_word, reading)
    pitch_str = get_pitch(k_word, furigana)
    return furigana, pitch_str


def main():
    dfrows = list(df.iterrows())
    for _, row in tqdm(dfrows):
        row_tags = clean_lesson_tag(row["lesson"])
        if not pd.isnull(row["kanji"]):
            if row["kanji"][0] == "〜" and row["word"][0] == "〜":
                row["kanji"] = row["kanji"][1:-1]
                row["word"] = row["kanji"][1:-1]
            if row["kanji"][-1] == "〜" and row["word"][-1] == "〜":
                row["kanji"] = row["kanji"][0:-2]
                row["word"] = row["kanji"][0:-2]

            furigana = get_furigana(row["kanji"], row["word"])
            pitch_str = get_pitch(row["kanji"], furigana)
            pitch_note = genanki.Note(
                model=genki_pitch_model,  # in constants.py
                fields=[
                    row["kanji"],
                    furigana,
                    row["english"],
                    row["pos"],
                    pitch_str,
                ],
                tags=row_tags,
            )
        else:
            # lmao this is kind of dumb
            pitch_str = get_pitch(row["word"], row["word"])
            pitch_note = genanki.Note(
                model=genki_pitch_model,
                fields=[row["word"], "", row["english"], row["pos"], pitch_str],
                tags=row_tags,
            )

        # pitch deck in constants.py
        genki_pitch_deck.add_note(pitch_note)

    genanki.Package(genki_pitch_deck).write_to_file(
        "~/files/genki-practice/anki-data/test-anki.apkg"
    )


if __name__ == "__main__":
    main()


# [\w ]*[0-9]*\%|[█▏▎▍▌▊▋▉▉]*[\w ]*|[ ]*[0-9/ ]*\[[0-9,:< \.a-z/]*\]\0
