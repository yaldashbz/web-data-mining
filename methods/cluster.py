import os
import pickle
from typing import Tuple

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from yellowbrick.cluster import KElbowVisualizer

from data_collection.utils import get_content
from methods.representation import TFIDFRepresentation, BertRepresentation, FasttextRepresentation
from methods.utils import plot_silhouette

_representations = {
    'tf-idf': TFIDFRepresentation,
    'bert': BertRepresentation,
    'fasttext': FasttextRepresentation
}


class ContentKMeanCluster:
    _PATH = '../models/kmeans'
    _MODEL = 'kmeans.pkl'
    _RESULT = 'result.json'

    def __init__(self, data, method: str = 'tf-idf', **repr_kwargs):
        self.data = data
        self.representation = _representations[method](data=data, **repr_kwargs)
        self.represented_df = self.representation.represent()
        self.k_means = None if data is not None else self.load_model(self.model_path)
        self.result_df = None if data is not None else self.load_result(self.result_path)

    @property
    def model_path(self):
        return os.path.join(self._PATH, self._MODEL)

    @property
    def result_path(self):
        return os.path.join(self._PATH, self._RESULT)

    def run(self, k: int = 2, save: bool = True):
        self.k_means = KMeans(
            n_clusters=k,
            random_state=1
        ).fit(self.represented_df)
        if save:
            self.save_model(self.model_path)
        return self.k_means

    def save_model(self, path: str):
        pickle.dump(self.k_means, open(path, 'wb'))

    def save_result(self, path: str):
        self.result_df.to_json(path)

    @classmethod
    def load_model(cls, path: str):
        return pickle.load(open(path, 'rb'))

    @classmethod
    def load_result(cls, path: str):
        return pd.read_json(path)

    def cluster(self, query: str):
        vector = self.representation.embed(query)
        labels = self.k_means.predict([vector])
        return labels[0]

    def get_clustered_data(self, cluster_id):
        return self.result_df[self.result_df.cluster_id == cluster_id]

    def _get_result(self):
        result = self.data
        for doc_id, cluster_id in enumerate(self.k_means.labels_):
            result[doc_id].update(cluster_id=cluster_id)
        return result

    def analyse(self, save: bool = True) -> pd.DataFrame:
        assert self.k_means

        result = self._get_result()
        result_df = pd.DataFrame(result)
        result_df['content'] = result_df['tokens'].apply(get_content)
        result_df.pop('tokens')
        self.result_df = result_df
        if save:
            self.save_result(self.result_path)
        return result_df

    def elbow_visualize(self, k_range: Tuple[int, int]):
        model = KMeans(random_state=1)
        visualizer = KElbowVisualizer(model, k=k_range).fit(self.represented_df)
        visualizer.show()

    def silhouette_evaluate(self, plot: bool = False):
        k = self.k_means.n_clusters
        df = self.represented_df.to_numpy()
        labels = self.k_means.predict(df)
        score = silhouette_score(df, labels)
        if plot:
            plot_silhouette(df, k, labels, score)
        return score

    def rss_evaluate(self):
        return self.k_means.inertia_
