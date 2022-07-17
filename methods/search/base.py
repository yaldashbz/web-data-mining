import os
from abc import ABC, abstractmethod
from typing import Optional

from data_collection.utils import TOKENS_KEY
from methods.search.utils import DataOut
from preprocess import PreProcessor


class BaseSearcher(ABC):
    def __init__(self, data, tokens_key: str = TOKENS_KEY):
        assert len(data) > 0
        assert tokens_key in data[0].keys()

        self.data = data
        self.tokens_key = tokens_key
        self.pre_processor = PreProcessor()

    @abstractmethod
    def search(self, query, k: int = 10) -> Optional[DataOut]:
        pass

    @classmethod
    def mkdir(cls, path):
        if not os.path.exists(path):
            os.mkdir(path)
