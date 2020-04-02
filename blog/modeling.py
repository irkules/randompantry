from collections import defaultdict
from pandas import DataFrame
from sklearn.decomposition import TruncatedSVD
from sklearn.neighbors import NearestNeighbors
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MultiLabelBinarizer, LabelEncoder, StandardScaler
from surprise import Dataset, KNNBaseline, Reader, SVDpp


class RecipeNet:
    def __init__(self):
        self.model = make_pipeline(
            StandardScaler(),
            MLPRegressor(
                hidden_layer_sizes=(100, 100),
                activation='relu',
                solver='sgd',
                alpha=0.0001,
                max_iter=200,
                random_state=2020,
                verbose=True,
                momentum=0.9
            )
        )
        self.recipe_le = LabelEncoder()

    def fit(self, reviews):
        reviews = DataFrame(reviews)
        reviews['user_id'] = LabelEncoder().fit_transform(reviews['user_id'].values)
        reviews['recipe_id'] = self.recipe_le.fit_transform(reviews['recipe_id'].values)
        exclude_recipe_ids = reviews.loc[reviews.user_id == 0, 'recipe_id'].values
        self.encoded_ids = [id for id in reviews['recipe_id'].unique() if id not in exclude_recipe_ids]
        return self.model.fit(
            X=reviews[['user_id', 'recipe_id']].values, 
            y=reviews['rating'].values
        )

    def predict(self, n=20):
        X_test = DataFrame({ 'user_id': [1] * len(self.encoded_ids), 'recipe_id': self.encoded_ids }).values
        y_pred = self.model.predict(X_test)
        pred_encoded_ids = (-y_pred).argsort()[:n]
        return self.recipe_le.inverse_transform(pred_encoded_ids)

class RecipeRecommender:
    def __init__(self, n_factors=20, n_epochs=20, lr_all=0.007, reg_all=0.02):
        self.model = SVDpp(n_factors=n_factors, n_epochs=n_epochs, lr_all=lr_all, reg_all=reg_all, random_state=2020)

    def fit(self, reviews):
        # SurPRISE supports only pandas DataFrame or folds as data input
        data = Dataset.load_from_df(
            DataFrame(reviews), 
            Reader(rating_scale=(1, 5))
        )
        self.trainset = data.build_full_trainset()
        self.testset = self.trainset.build_anti_testset()
        return self.model.fit(self.trainset)

    def predict(self, n=20):
        self.predictions = self.model.test(self.testset)
        recommended_dict = RecipeRecommender.get_top_n(self.predictions, n=n)
        return [id_tuple[0] for id_tuple in recommended_dict[1]]

    @staticmethod
    def get_top_n(predictions, n):
        top_n = defaultdict(list)
        for uid, iid, _, est, _ in predictions:
            top_n[uid].append((iid, est))
        for uid, user_ratings in top_n.items():
            user_ratings.sort(key=lambda x: x[1], reverse=True)
            top_n[uid] = user_ratings[:n]
        return top_n

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
            self.components = train
        return self.model.fit(self.components)

    def predict(self, recipe_id, recipe_ids, k=20):
        current_components = self.components[recipe_ids.index(recipe_id)]
        nearest_indices = self.model.kneighbors([current_components], return_distance=False)[0]
        nearest_ids = [recipe_ids[x] for x in nearest_indices]
        return nearest_ids[1:(k + 1)]

class NearestRecipesBaseline:
    def __init__(self, k=40):
        self.model = KNNBaseline(
            k=k,
            sim_options={ 'name': 'pearson_baseline', 'user_based': False },
            verbose=False
        )

    def fit(self, reviews):
        # SurPRISE supports only pandas DataFrame or folds as data input
        data = Dataset.load_from_df(
            DataFrame(reviews), 
            Reader(rating_scale=(1, 5))
        )
        trainset = data.build_full_trainset()
        return self.model.fit(trainset)

    def predict(self, recipe_id, k=20):
        inner_id = self.model.trainset.to_inner_iid(recipe_id)
        nearest_inner_ids = self.model.get_neighbors(inner_id, k=k)
        nearest_ids = [self.model.trainset.to_raw_iid(id) for id in nearest_inner_ids]
        return nearest_ids
