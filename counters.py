import copy  # For making deepcopies of dicts and stuff

######################################################################
# Define some constants

#
# Define a dictionary to convert between voiced and unvoiced forms
#
voiced = {
    # [k] -> [g]
    "か": "が",
    "き": "ぎ",
    "く": "ぐ",
    "け": "げ",
    "こ": "ご",
    # [s] -> [z]
    "さ": "ざ",
    "し": "じ",
    "す": "ず",
    "せ": "ぜ",
    "そ": "ぞ",
    # [t] -> [d]
    "た": "だ",
    "ち": "ぢ",
    "つ": "づ",
    "て": "で",
    "と": "ど",
    # [h] -> [b]
    "は": "ば",
    "ひ": "び",
    "ふ": "ぶ",
    "へ": "べ",
    "ほ": "ぼ",
    # [b] -> [p] # Ok I know this is kind of actually the reverse but
    "ば": "ぱ",
    "び": "ぴ",
    "ぶ": "ぷ",
    "べ": "ぺ",
    "ぼ": "ぽ",
}


#
# Sets of all of the phonemes by leading consonant
#
a_ = frozenset({"あ", "い", "う", "え", "お"})  # is this name good
k_ = frozenset({"か", "き", "く", "け", "こ"})
g_ = frozenset({voiced[mora] for mora in k_})
s_ = frozenset({"さ", "し", "す", "せ", "そ"})
z_ = frozenset({voiced[mora] for mora in s_})
t_ = frozenset({"た", "ち", "つ", "て", "と"})
d_ = frozenset({voiced[mora] for mora in t_})
n_ = frozenset({"な", "に", "ぬ", "ね", "の"})
h_ = frozenset({"は", "ひ", "ふ", "へ", "ほ"})
b_ = frozenset({voiced[mora] for mora in h_})
p_ = frozenset({voiced[mora] for mora in b_})
m_ = frozenset({"ま", "み", "む", "め", "も"})
y_ = frozenset({"や", "　", "ゆ", "　", "よ"})
r_ = frozenset({"ら", "り", "る", "れ", "ろ"})
w_ = frozenset({"わ", "　", "　", "　", "を"})

consonants = {a_, k_, g_, s_, z_, t_, d_, n_, h_, b_, p_, m_, y_, r_, w_}

#
# Sets of all of the phonemes by vowel
#
_a = frozenset(
    {"あ", "か", "が", "さ", "ざ", "た", "だ", "な", "は", "ば", "ぱ", "ま", "や", "ら", "わ"}
)
_i = frozenset(
    {"い", "き", "ぎ", "し", "じ", "ち", "ぢ", "に", "ひ", "び", "ぴ", "み", "　", "り", "　"}
)
_u = frozenset(
    {"う", "く", "ぐ", "す", "ず", "つ", "づ", "ぬ", "ふ", "ぶ", "ぷ", "む", "ゆ", "る", "　"}
)
_e = frozenset(
    {"え", "け", "げ", "せ", "ぜ", "て", "で", "ね", "へ", "べ", "ぺ", "め", "　", "れ", "　"}
)
_o = frozenset(
    {"お", "こ", "ご", "そ", "ぞ", "と", "ど", "の", "ほ", "ぼ", "ぽ", "も", "よ", "ろ", "を"}
)
vowels = {_a, _i, _u, _e, _o}

#
# Standard euphonic change involving glottal stops
#
glottal_prefixes = {
    1: "いっ",
    6: "ろっ",  # Not used with [s], [ɕ], [z], [ʑ], [t], [tɕ],
    8: "はっ",
    10: "じゅっ",  # じっ is also standard but I just picked one
}


def get_vowel(mora):
    """
    mora: a single hiragana character, like は

    example call:
        >>> get_cons_vowel_pair("は")
        _a
    """
    # Unpack the list comprehension because it's just a 1-element list
    (vset,) = [vset for vset in vowels if mora in vset]
    return vset


def get_cons(mora):
    """
    mora: a single hiragana character, like は

    example call:
        >>> get_cons_vowel_pair("は")
        h_
    """
    # Unpack the list comprehension because it's just a 1-element list
    (cset,) = [cset for cset in consonants if mora in cset]
    return cset


def get_cons_vowel_pair(mora):
    """
    mora: a single hiragana character, like は

    example call:
        >>> get_cons_vowel_pair("は")
        (h_, _a)


    Now, the actual input character can be obtaind by taking the
    intersection h_ && _a.
    """
    return (get_cons(mora), get_vowel(mora))


def morph_cons(mora, new_cons):
    """
    handles phonological morphing rules for swapping consonants out.
    This function will be defined

    E.g.,
    >>> morph("ほ", p_)
    "ぽ"
    """
    (new_mora,) = new_cons & get_vowel(mora)
    return new_mora


def morph_vowel(mora, new_vowel):
    """
    handles phonological morphing rules for swapping vowels out. Not
    sure if this is actually ever used in any capacity? But it was
    easy to write.

    E.g.,
    >>> morph("ほ", _u)
    "ふ"
    """
    (new_mora,) = get_cons(mora) & new_vowel
    return new_mora


######################################################################
# Common morphings
def to_p(mora):
    return morph_cons(mora, p_)


def to_b(mora):
    return morph_cons(mora, b_)


def to_g(mora):
    return morph_cons(mora, g_)


def to_z(mora):
    return morph_cons(mora, z_)


######################################################################
# Ok now actually for the counter words
#
# Define the standard counter word numeral rule things
standard_prefixes = {
    1: "いち",
    2: "に",
    3: "さん",
    4: "よん",
    5: "ご",
    6: "ろく",
    7: "なな",
    8: "はち",
    9: "きゅう",
    10: "じゅう",
    "question": "なん",
}

# Class for each
class Counter:
    def __init__(self, counter_word, prefixes=dict(), morph_rules=dict()):
        """
        counter_word: The base counter word string.
            E.g., 「本」(sticks / pens / pencils / etc.)

        prefixes: Before doing actual phonological morphing, sometimes
                  there's a standard prefix for the counter words.
                  This dict provides that. Keys are numbers, values
                  are the associated strings.
            E.g., prefixes = {
                1: "いっ",
                6: "ろっ",  # Not used with [s], [ɕ], [z], [ʑ], [t], [tɕ],
                8: "はっ",
                10: "じゅっ",  # じっ is also standard but I just picked one
            }

        morph_rules: a dictionary that gives any phonological morphing
                 rules that might occur.
            E.g., morph_rules = { # The rules for 「本」
                1 : p_,
                3 : b_,
                6 : p_,
                8 : p_,
                10 : p_,
                "question : b_,
            }
        """
        # Fill in all the empty entries and things
        for i in range(1, 11):
            if i not in prefixes.keys():
                prefixes[i] = standard_prefixes[i]
            if i not in morph_rules.keys():
                morph_rules[i] = lambda x: x  # Give it the identity map

        first_mora = counter_word[0]
        rest_of_cw = counter_word[1:]
        new_map = dict()

        # Union all of the things we might possibly need to include as
        # special cases in our map
        nums = (
            {i for i in range(1, 11)}
            | {"question"}
            | set(morph_rules.keys())
            | set(prefixes.keys())
        )

        for i in range(1, 11):
            # print(morph_rules[i](first_mora))
            new_map[i] = prefixes[i] + morph_rules[i](first_mora) + rest_of_cw
            # print(new_map[i])
        self.counter_word = counter_word
        self.qdict = new_map
        return

    def quantity(self, n):
        """
        This is the function for getting the appropriate pronunciation
        of a counter word. Does _not_ treat exceptional cases, such as
        years of age, small items, and dates of the month. For those,
        one should override the method manually.
        """
        if n <= 0:
            assert False  # Just threw this in beacuse I doubt
            # we'll ever want to practice counting nonpositive
            # quantities unless we're talking about my bank
            # balance
        else:
            if n == 10:
                # print(self.qdict[n])
                return self.qdict[n]
            else:
                m = n % 10  # Only want trailing digit
                # print(self.qdict[m])
                return self.qdict[m]


######################################################################
# Below: all of the columns from page 380 of Genki.

# Regular counters (no special rules)
dollar_counter = Counter("ドル")
yen_counter = Counter("えん")
sheet_counter = Counter("まい")
degree_counter = Counter("ど")
ten_counter = Counter("じゅう")
ten_thousand_counter = Counter("まん")


# Months
# --------------------------------------------------------------------
month_prefixes = {
    4: "し",
    7: "しち",
    9: "く",
}
month_counter = Counter("がつ", prefixes=month_prefixes)


# Hours
# --------------------------------------------------------------------
hours_prefixes = {4: "よ", 7: "しち", 9: "く"}
oclock_counter = Counter("じ", prefixes=hours_prefixes)
hours_counter = Counter("じかん", prefixes=hours_prefixes)

# Years, people
# --------------------------------------------------------------------
year_and_people_prefixes = {4: "よ"}

# For saying stuff like "it was the year 2003"
year_counter = Counter("ねん", prefixes=year_and_people_prefixes)

# For saying stuff like "that was 2003 years ago"
years_counter = Counter("ねんかん", prefixes=year_and_people_prefixes)

# Counting people has some special casework.
naive_people_counter = Counter("にん", prefixes=year_and_people_prefixes)


def people_quantifier(n):
    if n == 1:
        return "ひとり"
    elif n == 2:
        return "ふたり"
    else:
        return naive_people_counter.quantity(n)


people_counter = Counter("にん", prefixes=year_and_people_prefixes)
people_counter.quantity = people_quantifier


# Minutes
# --------------------------------------------------------------------
minute_prefixes = copy.deepcopy(glottal_prefixes)
minute_prefixes[8] = "*" + minute_prefixes[8]  # * == optional

# Construct dict for phonological morphing
minute_morph_rules = dict()
for i in [1, 3, 4, 6, 8, 10, "question"]:
    minute_morph_rules[i] = to_p  # All of em change to p

# For things like "it's 10:23"
minute_counter = Counter("ふん", prefixes=minute_prefixes, morph_rules=minute_morph_rules)

# For things like "That took 10 hours and 23 minuts"
minutes_counter = Counter(
    "ふんかん", prefixes=minute_prefixes, morph_rules=minute_morph_rules
)


# Sticks, cups, animals, hundreds
# --------------------------------------------------------------------
stick_prefixes = glottal_prefixes
stick_morph_rules = {1: to_p, 3: to_b, 6: to_p, 8: to_p, 10: to_p, "question": to_b}

stick_counter = Counter("ほん", prefixes=stick_prefixes, morph_rules=stick_morph_rules)
cup_counter = Counter("はい", prefixes=stick_prefixes, morph_rules=stick_morph_rules)
animal_counter = Counter("ひき", prefixes=stick_prefixes, morph_rules=stick_morph_rules)
hundered_counter = Counter(
    "ひゃく", prefixes=stick_prefixes, morph_rules=stick_morph_rules
)


# Pages, pounds
# --------------------------------------------------------------------
page_prefixes = copy.deepcopy(glottal_prefixes)
for i in [1, 6, 8]:
    page_prefixes[i] = "*" + page_prefixes[i]

page_counter = Counter("ページ", page_prefixes)
pound_counter = Counter("ポンド", page_prefixes)  # same prefixes


# Months, lesson, times, small items
# --------------------------------------------------------------------
month_prefixes = glottal_prefixes
months_counter = Counter("かげつ", prefixes=month_prefixes)
lesson_counter = Counter("か", prefixes=month_prefixes)
times_counter = Counter("かい", prefixes=month_prefixes)
small_items_counter = Counter("こ", prefixes=month_prefixes)


# Floors, houses
# --------------------------------------------------------------------
floor_prefixes = glottal_prefixes
floor_morph_rules = {1: to_g, "question": to_g}

floor_counter = Counter("かい", prefixes=floor_prefixes, morph_rules=floor_morph_rules)
houses_counter = Counter("けん", prefixes=floor_prefixes, morph_rules=floor_morph_rules)

# Cents, weks, books
# --------------------------------------------------------------------
cent_prefixes = copy.deepcopy(glottal_prefixes)
del cent_prefixes[6]  # No glottal stop on 6 for some reason

cents_counter = Counter("セント", prefixes=cent_prefixes)
weeks_counter = Counter("しゅうかん", prefixes=cent_prefixes)
books_counter = Counter("さつ", prefixes=cent_prefixes)
years_of_age_counter = Counter("さい", prefixes=cent_prefixes)


# Shoes, thousands
# --------------------------------------------------------------------
shoes_prefixes = cent_prefixes
shoes_morph_rules = {3: to_z, "question": to_z}

shoes_counter = Counter("そく", prefixes=shoes_prefixes, morph_rules=shoes_morph_rules)
thousands_counter = Counter(
    "せん", prefixes=shoes_prefixes, morph_rules=shoes_morph_rules
)

# Letters, street addresses
# --------------------------------------------------------------------
letters_prefixes = cent_prefixes
letters_counter = Counter("つう", prefixes=letters_prefixes)
street_address_counter = Counter("ちょうめ", prefixes=letters_prefixes)
