import json
import requests

from bs4 import BeautifulSoup
from tqdm import tqdm
from copy import deepcopy

from constants import *


def katakana_to_hiragana(k_str):
    new_str = ""
    for char in k_str:
        if char in convert_kana:
            new_str += convert_kana[char]
        else:
            new_str += char
    return new_str


def ingest_data():
    """
    Given `test.json`, a json-exported copy of the anki deck we want
    to grab pitch accent things for, load it in.
    """
    with open("/tmp/test.json", "r") as f:
        return json.load(f)


def get_pitches_for_card(query_term):
    query_str = str(query_term.encode()).replace(r"\x", "%")[2:-1]
    query_url = search_url + query_str
    page = requests.get(query_url)
    soup = BeautifulSoup(page.content, "html.parser")

    return soup.find_all("span", class_="accented_word")


def separate_readings(furigana_string):
    list_of_readings = furigana_string.split("、")
    new_list = []
    for reading in list_of_readings:
        new_reading = ""
        for char in reading:
            if char in kana_str:
                new_reading += char
        new_list += [new_reading]
    return new_list


def pitch_html_to_reading(pitch_html):
    """
    Concatenate individual mora together in an accented word
    """
    return "".join([_.text for _ in pitch_html.find_all("span", class_="char")])


def match_to_reading(unprocessed_readings, unprocessed_pitches):
    readings = separate_readings(unprocessed_readings)
    pitch_readings = [pitch_html_to_reading(_) for _ in unprocessed_pitches]

    output_pitch_htmls = []
    for reading in readings:
        for (i, pitch_reading) in enumerate(pitch_readings):
            if katakana_to_hiragana(reading) == katakana_to_hiragana(pitch_reading):
                output_pitch_htmls += [str(unprocessed_pitches[i])]

    output_str = "\n".join(output_pitch_htmls).replace("<", "&lt;").replace(">", "&gt;")

    return output_str


def clear_pitches():
    json_dat = ingest_data()
    new_dat = deepcopy(json_dat)
    for (i, card) in enumerate(json_dat["notes"]):
        new_dat["notes"][i]["fields"][-1] = ""

    with open("/tmp/test.json", "w") as f:
        write_me = json.dumps(new_dat, indent=4, sort_keys=True)
        f.write(write_me)


def clear_nas():
    json_dat = ingest_data()
    new_dat = deepcopy(json_dat)
    for (i, card) in enumerate(json_dat["notes"]):
        if card["fields"][-1] == "N/A":
            new_dat["notes"][i]["fields"][-1] = ""

    with open("/tmp/test.json", "w") as f:
        write_me = json.dumps(new_dat, indent=4, sort_keys=True)
        f.write(write_me)


def main():
    json_dat = ingest_data()
    new_dat = deepcopy(json_dat)

    try:
        exceptions = []
        for (i, card) in enumerate(tqdm(json_dat["notes"])):
            query_term = card["fields"][0].split("、")[0]  # remove duplicates
            if card["fields"][-1] == "N/A":
                exceptions += [query_term]
            elif not card["fields"][-1]:
                pitch_accents = get_pitches_for_card(query_term)
                pitch_str = match_to_reading(card["fields"][1], pitch_accents)
                if not pitch_str:
                    print(f"exception: {query_term}")
                    exceptions += [query_term]
                    new_dat["notes"][i]["fields"][-1] = "N/A"
                else:
                    new_dat["notes"][i]["fields"][-1] = pitch_str

    except KeyboardInterrupt:
        pass

    with open("/tmp/test.json", "w") as f:
        write_me = json.dumps(new_dat, indent=4, sort_keys=True)
        f.write(write_me)

    with open("/tmp/exceptions.txt", "w") as f:
        write_me = str(exceptions).replace(", ", "\n").replace("[", "").replace("]", "")
        f.write(write_me)

    print(f"There were {len(exceptions)} exceptions.")


def test():
    pitch_accents = get_pitches_for_card("十")
    reading = "十[とお]、 十[じゅう]"
    pitch_str = match_to_reading(reading, pitch_accents)
    if not pitch_str:
        print(f"exception: {query_term}")
    else:
        print(pitch_str)


def test2():
    pitch_accents = get_pitches_for_card("火")
    reading = "ひ"
    pitch_str = match_to_reading(reading, pitch_accents)
    if not pitch_str:
        print(f"exception: {query_term}")
    else:
        print(pitch_str)


if __name__ == "__main__":
    main()
    # test()
    # test2()
