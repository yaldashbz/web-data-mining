from sklearn.cluster import KMeans

from methods.representation import TFIDFRepresentation, BertRepresentation

_representations = {
    'tf-idf': TFIDFRepresentation,
    'bert': BertRepresentation
}


class ContentKMeanCluster:
    def __init__(self, data, method: str = 'tf-idf'):
        self.representation = _representations[method](data)
        self.represented_df = self.representation.represent()

    def _kmeans_fit(self, k: int = 2):
        kmeans = KMeans(n_clusters=k, random_state=1)
        return kmeans.fit(self.represented_df)

    def run(self, k: int = 2):
        return dict(estimator=self._kmeans_fit(k), k=k)
