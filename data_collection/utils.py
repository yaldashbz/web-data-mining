from itertools import chain
from typing import List, Tuple
from nltk import FreqDist

DIVIDER = ' '

CATEGORIES = [
    'religion',
    'sports', 'drink',
    'financial', 'health', 'literature',
    'social networks', 'food', 'history',
    'animals', 'news', 'science', 'movies',
    'music', 'games', 'computer',
    'football', 'basketball', 'volleyball',
    'university', 'national', 'politics'
]


def get_keywords(tokens: List[List[str]], count: int = 20) -> List[Tuple]:
    words = get_words(tokens)
    return FreqDist(words).most_common(count)


def get_doc_content(doc):
    return DIVIDER.join(get_sentences(doc['tokens']))


def get_contents(data: List):
    return [get_doc_content(doc) for doc in data]


def get_sentences(tokens: List[List[str]]):
    return [DIVIDER.join(words) for words in tokens]


def get_doc_sentences(doc):
    return get_sentences(doc['tokens'])


def get_words(tokens: List[List[str]]):
    return list(chain(*tokens))


def get_doc_words(doc):
    return get_words(doc['tokens'])
