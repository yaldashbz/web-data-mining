import json
from dataclasses import dataclass
from typing import List, Tuple

from preprocess import PreProcessor
from data_collection.utils import get_keywords, DIVIDER


@dataclass
class EngineData:
    url: str
    tokens: List[List[str]]
    keywords: List[Tuple]
    content: str

    def __init__(self, url, content):
        self.url = url
        self.content = content
        preprocessor = PreProcessor()
        self.tokens = preprocessor.process(content, stopwords_removal=False, min_len=0)
        keyword_tokens = preprocessor.normalize(self.tokens, stopwords_removal=True)
        processed_content = DIVIDER.join([DIVIDER.join(sentence) for sentence in keyword_tokens])
        self.keywords = get_keywords(processed_content)

    def __hash__(self):
        return hash(f'{self.url} - {self.content}')

    @classmethod
    def _convert(cls, data: List) -> List:
        return [{'url': doc.url, 'tokens': doc.tokens, 'keywords': doc.keywords} for doc in data]

    @classmethod
    def _cleanup(cls, data: List) -> List:
        return [doc for doc in data if doc.tokens]

    @classmethod
    def save(cls, data: List, path: str):
        data = cls._cleanup(data)
        json.dump(cls._convert(data), open(path, 'w+'))
