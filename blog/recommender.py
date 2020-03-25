from surprise import Dataset, Reader, SVD, SVDpp
from collections import defaultdict
from blog import db
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
        # self.model = SVDpp(
        #     n_factors=n_factors, 
        #     n_epochs=n_epochs,
        #     lr_all=lr_all,
        #     reg_all=reg_all,
        #     lr_bu=lr_bu, lr_bi=lr_bi, lr_pu=lr_pu, lr_qi=lr_qi, lr_yj=lr_yj,
        #     reg_bu=reg_bu, reg_bi=reg_bi, reg_pu=reg_pu, reg_qi=reg_qi, reg_yj=reg_yj,
        #     random_state=2020
        # )
        self.model = SVD(
            n_factors=n_factors, 
            n_epochs=n_epochs,
            random_state=2020
        )

    def fit(self, reviews):
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(reviews, reader)
        self.trainset = data.build_full_trainset()
        self.testset = self.trainset.build_anti_testset()
        return self.model.fit(self.trainset)

    def predict(self, reviews):
        self.predictions = self.model.test(self.testset)
        has_rated = (reviews.user_id == 1).any()
        if has_rated:
            top_n_recipes_ids = RecipeRecommender.get_top_n(self.predictions)
            recommended_recipe_ids = np.array(top_n_recipes_ids[1], dtype='uint')[:, 0]
            # Cache predictions in database
            db.update_home_cache(['recommended'], [list(recommended_recipe_ids)])
            return recommended_recipe_ids
        else:
            return []

    @staticmethod
    def get_top_n(predictions, n=20):
        top_n = defaultdict(list)
        for uid, iid, _, est, _ in predictions:
            top_n[uid].append((iid, est))
        for uid, user_ratings in top_n.items():
            user_ratings.sort(key=lambda x: x[1], reverse=True)
            top_n[uid] = user_ratings[:n]
        return top_n

