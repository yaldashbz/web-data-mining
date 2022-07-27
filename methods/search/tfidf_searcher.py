from typing import Optional

import numpy as np

from data_collection.utils import TOKENS_KEY
from methods.representation import TFIDFRepresentation
from methods.search.base import BaseSearcher
from methods.search.query_expansion import FasttextQueryExpansion
from methods.search.utils import DataOut
from methods.utils import cosine_sim


class TFIDFSearcher(BaseSearcher):
    def __init__(
            self, data,
            qe: FasttextQueryExpansion,
            tokens_key: str = TOKENS_KEY,
            representation: Optional[TFIDFRepresentation] = None
    ):
        super().__init__(data, qe, tokens_key)
        self.representation = TFIDFRepresentation(data, tokens_key=tokens_key) \
            if not representation else representation

    def search(self, query, k: int = 10, use_qe: bool = False) -> Optional[DataOut]:
        if use_qe:
            query = self.qe.expand_query(query.lower().split())
        scores = list()
        vector = self.representation.embed(query)
        for doc in self.representation.matrix.A:
            scores.append(cosine_sim(vector, doc))

        return DataOut(self._get_results(scores, k))

    def _get_results(self, scores, k):
        out = np.array(scores).argsort()[-k:][::-1]
        return [dict(
            index=index,
            url=self.data[index]['url'],
            score=scores[index]
        ) for index in out]
