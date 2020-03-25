from sklearn.neighbors import NearestNeighbors
from surprise import Dataset, KNNBaseline, Reader
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import MultiLabelBinarizer
import numpy as np


class NearestRecipes:
    def __init__(self, k=40, reduce=True):
        self.k = k
        self.model = NearestNeighbors(n_neighbors=k, n_jobs=-1)
        self.reduce = reduce
        if self.reduce:
            self.mlb = MultiLabelBinarizer(sparse_output=True)
            self.tsvd = TruncatedSVD(n_components=100, random_state=2020)

    def fit(self, train):
        if self.reduce:
            matrix = self.mlb.fit_transform(train)
            self.components = self.tsvd.fit_transform(matrix)
        else:
            self.components = np.array(list(train))
        return self.model.fit(self.components)

    def predict(self, recipe_id, recipe_ids):
        current_components = self.components[recipe_ids == recipe_id]
        nearest_indices = self.model.kneighbors(current_components, return_distance=False)[0]
        nearest_ids = [recipe_ids[x] for x in nearest_indices]
        return nearest_ids[1:21]

class NearestRecipesBaseline:
    def __init__(self, k=40):
        self.model = KNNBaseline(
            k=k,
            sim_options={ 'name': 'pearson_baseline', 'user_based': False },
            verbose=False
        )

    def fit(self, reviews):
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(reviews, reader)
        trainset = data.build_full_trainset()
        return self.model.fit(trainset)

    def predict(self, recipe_id):
        inner_id = self.model.trainset.to_inner_iid(recipe_id)
        nearest_inner_ids = self.model.get_neighbors(inner_id, k=20)
        nearest_ids = [self.model.trainset.to_raw_iid(id) for id in nearest_inner_ids]
        return nearest_ids
