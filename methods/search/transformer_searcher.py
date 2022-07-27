from typing import Optional

import faiss
import numpy as np

from data_collection.utils import TOKENS_KEY
from methods import FasttextQueryExpansion
from methods.representation import BertRepresentation
from methods.search.base import BaseSearcher
from methods.search.utils import DataOut


class TransformerSearcher(BaseSearcher):
    def __init__(
            self, data,
            qe: FasttextQueryExpansion,
            load: bool = False, tokens_key: str = TOKENS_KEY,
            representation: Optional[BertRepresentation] = None
    ):
        super().__init__(data, qe, tokens_key)
        self.representation = BertRepresentation(
            data=data, load=load, tokens_key=tokens_key
        ) if not representation else representation
        self.index = self._get_index(self.representation.embeddings)

    @classmethod
    def _get_index(cls, embeddings):
        index = faiss.IndexIDMap(faiss.IndexFlatL2(embeddings.shape[1]))
        index.add_with_ids(embeddings, np.array(range(len(embeddings))).astype('int64'))
        return index

    def search(self, query, k: int = 10, use_qe: bool = False) -> Optional[DataOut]:
        if use_qe:
            query = self.qe.expand_query(query.lower().split())
        vector = self.representation.embed(query)
        distances, indexes = self.index.search(
            np.array(vector.reshape(1, -1)).astype('float32'), k=k)
        return DataOut(self._get_results(distances, indexes))

    def _get_results(self, distances, indexes):
        indexes = indexes.flatten().tolist()
        distances = distances.flatten().tolist()
        return [dict(
            url=self.data[index]['url'],
            score=1 - distances[i] / 2
        ) for i, index in enumerate(indexes)]
