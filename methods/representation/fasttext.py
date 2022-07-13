import re
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from gensim.models.fasttext import FastText

from data_collection.utils import get_doc_words, TOKENS_KEY
from methods.representation import BaseRepresentation


class FasttextRepresentation(BaseRepresentation):
    _EPOCHS = 6
    _MODEL_PATH = '../models'
    _MODEL_FILE = 'fasttext.model'

    def __init__(
            self, data,
            train: bool = True,
            min_count: int = 4,
            tokens_key: str = TOKENS_KEY
    ):
        super().__init__(data, tokens_key)
        path = os.path.join(self._MODEL_PATH, self._MODEL_FILE)
        if not (train or os.path.exists(path)):
            raise ValueError

        self.fasttext = self._get_fasttext(train, min_count, path)
        if train:
            self._train()
            self._save_model()
        self.doc_embedding_avg = self._get_doc_embedding_avg()

    @classmethod
    def _get_fasttext(cls, train: bool, min_count: int, path: str):
        return FastText(
            sg=1, window=10, min_count=min_count,
            negative=15, min_n=2, max_n=5
        ) if train else FastText.load(path)

    def _train(self):
        tokens = [get_doc_words(doc, key=self.tokens_key) for doc in self.data]
        self.fasttext.build_vocab(tokens)
        self.fasttext.train(
            tokens,
            epochs=self._EPOCHS,
            total_examples=self.fasttext.corpus_count,
            total_words=self.fasttext.corpus_total_words
        )

    def _save_model(self):
        if not os.path.exists(self._MODEL_PATH):
            os.mkdir(self._MODEL_PATH)
        self.fasttext.save(os.path.join(self._MODEL_PATH, self._MODEL_FILE))

    def _get_doc_embedding_avg(self):
        docs_avg = dict()
        for index, doc in tqdm(enumerate(self.data)):
            words = get_doc_words(doc, key=self.tokens_key)
            docs_avg[index] = np.mean([
                self.fasttext.wv[word] for word in words if re.fullmatch('\\w+', word)
            ], axis=0)
        return docs_avg

    def represent(self) -> pd.DataFrame:
        return pd.DataFrame(
            data=self.doc_embedding_avg.values(),
            index=self.doc_embedding_avg.keys()
        )
