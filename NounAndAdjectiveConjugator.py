from japaneseverbconjugator.src.constants.EnumeratedTypes import (
    Tense,
    Polarity,
)

# --------------------------------------------------------------------
# Short forms
def noun_short_form(dict_form, tense, polarity):
    if tense == Tense.PAST:
        if polarity == Polarity.NEGATIVE:
            return dict_form + "じゃなかった"
        else:
            return dict_form + "だった"
    else:
        if polarity == Polarity.NEGATIVE:
            return dict_form + "じゃない"
        else:
            return dict_form + "だ"


# irregular adjective
def irr_adj_short_form(dict_form, tense, polarity):
    # Get the part that comes before the いい
    stem = dict_form[:-2]
    if tense == Tense.PAST:
        if polarity == Polarity.NEGATIVE:
            return stem + "よくなかった"
        else:
            return stem + "よかった"
    else:
        if polarity == Polarity.NEGATIVE:
            return stem + "よくない"
        else:
            return stem + "いい"


def i_adj_short_form(dict_form, tense, polarity):
    if tense == Tense.PAST:
        if polarity == Polarity.NEGATIVE:
            return dict_form[:-1] + "くなかった"
        else:
            return dict_form[:-1] + "かった"
    else:
        if polarity == Polarity.NEGATIVE:
            return dict_form[:-1] + "くない"
        else:
            return dict_form


# Na conjugates the same way as noun
def na_adj_short_form(dict_form, tense, polarity):
    return noun_short_form(dict_form, tense, polarity)


# --------------------------------------------------------------------
# Long forms
def noun_long_form(dict_form, tense, polarity):
    if tense == Tense.PAST:
        if polarity == Polarity.NEGATIVE:
            return dict_form + "じゃありませんでした"
        else:
            return dict_form + "でした"
    else:
        if polarity == Polarity.NEGATIVE:
            return dict_form + "じゃありませんです"
        else:
            return dict_form + "です"


# irregular adjective
def irr_adj_long_form(dict_form, tense, polarity):
    return irr_adj_short_form(dict_form, tense, polarity) + "です"


def i_adj_long_form(dict_form, tense, polarity, colloquial=False):
    if polarity == Polarity.POSITIVE:
        if tense == Tense.PAST:
            return dict_form[:-1] + "かったです"
        else:
            return dict_form + "です"
    else:
        if colloquial:
            return i_adj_short_form(dict_form, tense, polarity) + "です"
        else:
            if tense == Tense.PAST:
                return dict_form[:-1] + "くありませんでした"
            else:
                return dict_form[:-1] + "くありません"


# Na conjugates the same way as noun
# TODO: make colloquial vs conservative consistent with politeness
# levels defined in the verb conjugation module
def na_adj_long_form(dict_form, tense, polarity, colloquial=False):
    if polarity == Polarity.POSITIVE:
        if tense == Tense.PAST:
            return dict_form + "でした"
        else:
            return dict_form + "です"
    else:
        if colloquial:
            return na_adj_short_form(dict_form, tense, polarity) + "です"
        else:
            return noun_long_form(dict_form, tense, polarity)


# --------------------------------------------------------------------
# Te form
def noun_te_form(dict_form):
    return dict_form + "で"


def irr_adj_te_form(dict_form):
    return dict_form[:-2] + "よくて"


def i_adj_te_form(dict_form):
    return dict_form[:-1] + "くて"


def na_adj_te_form(dict_form):
    return noun_te_form(dict_form)


######################################################################
### Everything below here is TODO


# Haven't implemented this yet but theoretically in the future we'll
# use it when we make everything object oriented and declare lists of
# valid adjectives / etc. to use with a given noun
# class Noun:
#     def __init__(self, dict_form):
#         self.dict_form = dict_form
#         return

#     def pre_no_specifiers(self, prefix):
#         """
#         <prefix> の <self>.
#         """
#         return

#     def post_no():
#         """

#         """
#         return


# class Adjective(Noun):
#     def __init__(dict_form):
#         return


# def polite_form(adj, adj_class, tense, polarity):
#     """
#     adj: a string representing your chosen adjective. E.g., "さむい".
#     """
#     return
