from abc import ABC, abstractmethod
from typing import Optional

from data_collection.utils import TOKENS_KEY
from methods.search.query_expansion import FasttextQueryExpansion
from methods.search.utils import DataOut
from preprocess import PreProcessor


class BaseSearcher(ABC):
    def __init__(self, data, qe: FasttextQueryExpansion, tokens_key: str = TOKENS_KEY):
        assert len(data) > 0
        assert tokens_key in data[0].keys()

        self.data = data
        self.tokens_key = tokens_key
        self.pre_processor = PreProcessor()
        self.qe = qe

    @abstractmethod
    def search(self, query, k: int = 10) -> Optional[DataOut]:
        pass
