import json
import genanki
import requests

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


def get_furigana(kanji_word, reading):
    orig_kanji_word = kanji_word
    kanji_word, reading = clean_word(kanji_word), clean_word(reading)

    kanji_parts = [char for char in kanji_word if char not in kana_str]

    # The [2:-1] trims out the `b'......'`
    query_str = str(kanji_word.encode()).replace(r"\x", "%")[2:-1]
    query_url = base_jisho_url + query_str
    page = requests.get(query_url)
    soup = BeautifulSoup(page.content, "html.parser")

    # When we have a compound word where the individual parts are
    # recognized (but not the whole), it gives us one of these
    zen_bar = soup.find_all(id="zen_bar")

    anki_furigana_string = ""

    zen_bar_words = []

    if zen_bar:
        # print("fuck ugh")
        print(f"zen bar encountered on {kanji_word}")
        zen_bar_words += [orig_kanji_word]
        # bar_contents = zen_bar[0]
        # words = bar_contents.find_all("li", class_="clearfix japanese_word")
        # for word in words:
        #     furigana_parts = word.find_all("span", class_="japanese_word__furigana")
        #     if not furigana_parts:
        #         anki_furigana_string += f"{filter_non_kana(word.text)}"
        #     else:

        # TODO: Complete this
    else:
        candidates = soup.find_all("div", class_="concept_light-representation")

        for candidate in candidates:
            cand_reading = filter_non_kana(candidate.text)

            if cand_reading == reading:
                furigana_parts = [
                    _.text
                    for _ in candidate.find("span", class_="furigana").find_all(
                        "span", class_="kanji"
                    )
                ]

                try:
                    assert len(furigana_parts) == len(kanji_parts)
                except:
                    print(f"Assertion error! {kanji_word} {furigana_parts}")

                pairs = zip(furigana_parts, kanji_parts)

                j = 0
                for char in cand_reading:
                    if char not in kana_str:
                        anki_furigana_string += f"{pairs[j][1]}[{pairs[j][0]}] "
                        j += 1
                    else:
                        anki_furigana_string += char
                # for f_part, k_part in zip(furigana_parts, kanji_parts):
                #     anki_furigana_string += f"{k_part}[{f_part}] "

    return anki_furigana_string


def main():
    for _, row in tqdm(df.iterrows()):
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
