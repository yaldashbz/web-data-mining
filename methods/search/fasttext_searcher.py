from typing import Optional

from data_collection.utils import TOKENS_KEY
from methods.representation import FasttextRepresentation
from methods.search.base import BaseSearcher
from methods.search.query_expansion import FasttextQueryExpansion
from methods.search.utils import DataOut
from methods.utils import cosine_sim


class FasttextSearcher(BaseSearcher):
    def __init__(
            self, data,
            qe: FasttextQueryExpansion,
            train: bool = True, load: bool = False,
            min_count: int = 1, tokens_key: str = TOKENS_KEY,
            root: str = 'models', folder: str = 'fasttext',
            representation: Optional[FasttextRepresentation] = None
    ):
        super().__init__(data, qe, tokens_key)
        self.representation = FasttextRepresentation(
            data, train=train, load=load,
            min_count=min_count, tokens_key=tokens_key,
            root=root, folder=folder
        ) if not representation else representation

    def search(self, query, k: int = 10, use_qe: bool = False) -> Optional[DataOut]:
        if use_qe:
            query = self.qe.expand_query(query.lower().split())
        query_embedding_avg = self.representation.embed(query)
        similarities = self._get_similarities(query_embedding_avg, k)
        return DataOut(self._get_result(similarities))

    def _get_similarities(self, query_embedding, k):
        similarities = dict()
        for index, embedding in self.representation.doc_embedding_avg.items():
            similarities[index] = cosine_sim(embedding, query_embedding)
        return sorted(similarities.items(), key=lambda x: x[1])[::-1][:k]

    def _get_result(self, similarities):
        return [dict(
            url=self.data[index]['url'],
            score=score
        ) for index, score in similarities]
