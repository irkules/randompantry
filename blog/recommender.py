from surprise import Dataset, KNNBaseline, Reader, SVDpp
from .models import Recipe, Review
from collections import defaultdict
from . import db
import numpy as np

class RecipeRecommender:
    def __init__(
            self,
            n_factors=20,
            n_epochs=20,
            lr_all=0.007,
            reg_all=0.02,
            lr_bu=None, lr_bi=None, lr_pu=None, lr_qi=None, lr_yj=None,
            reg_bu=None, reg_bi=None, reg_pu=None, reg_qi=None, reg_yj=None
        ):
        self.model = SVDpp(
            n_factors=n_factors, 
            n_epochs=n_epochs,
            lr_all=lr_all,
            reg_all=reg_all,
            lr_bu=lr_bu, lr_bi=lr_bi, lr_pu=lr_pu, lr_qi=lr_qi, lr_yj=lr_yj,
            reg_bu=reg_bu, reg_bi=reg_bi, reg_pu=reg_pu, reg_qi=reg_qi, reg_yj=reg_yj
        )

    def fit(self, data_frame):
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(data_frame, reader)
        self.trainset = data.build_full_trainset()
        self.testset = trainset.build_anti_testset()
        return self.model.fit(trainset)

    def predict(self, testset):
        return self.model.test(testset)

    def get_recommended_ids(self, reviews_data_frame):
        reviews = reviews_data_frame[['user_id', 'recipe_id', 'rating']]
        user_id = 1
        has_rated = (reviews.user_id == user_id).any()
        if has_rated:
            self.fit(reviews_data_frame)
            predictions = self.predict(self.testset)
            top_n = self.get_top_n(predictions)
            recommended_ids = np.array(top_n[user_id])[:, 0]
            return recommended_ids
        else:
            return []

    def get_top_n(self, predictions, n = 15):
        top_n = defaultdict(list)
        for uid, iid, _, est, _ in predictions:
            top_n[uid].append((iid, est))
        for uid, user_ratings in top_n.items():
            user_ratings.sort(key=lambda x: x[1], reverse=True)
            top_n[uid] = user_ratings[:n]
        return top_n

    def get_recommended(self, recommended_ids):
        recommended_recipes_data_frame = db.get_recipes(rec_ids=recommended_ids)
        recommended = recommended_recipes_data_frame[['id', 'name', 'description', 'img_url']]
        recommended = [{ 'id': x[0], 'name': x[1], 'desc': x[2], 'img_url': x[3] } for x in recommended.values]
        return recommended
