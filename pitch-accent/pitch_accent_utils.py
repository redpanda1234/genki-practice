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


def get_pitches_for_term(query_term, base_url=base_ojad_url):
    query_str = str(query_term.encode()).replace(r"\x", "%")[2:-1]
    query_url = base_url + query_str
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


def get_pitch(query_term, reading):
    pitch_accents = get_pitches_for_term(query_term)
    pitch_str = match_to_reading(reading, pitch_accents)
    # if not pitch_str:
    #     print(reading)
    # print(f"exception: {query_term}")
    # TODO: Add a way to track exceptions

    return pitch_str
