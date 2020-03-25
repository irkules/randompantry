from surprise import Dataset, KNNBaseline, Reader, SVD, SVDpp
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
        #     reg_bu=reg_bu, reg_bi=reg_bi, reg_pu=reg_pu, reg_qi=reg_qi, reg_yj=reg_yj
        # )
        self.model = SVD(
            n_factors=n_factors, 
            n_epochs=n_epochs
        )

    def fit(self, data_frame):
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(data_frame, reader)
        self.trainset = data.build_full_trainset()
        self.testset = self.trainset.build_anti_testset()
        return self.model.fit(self.trainset)

    def predict(self, data_frame):
        self.predictions = self.model.test(self.testset)
        has_rated = (data_frame.user_id == 1).any()
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

    @staticmethod
    def get_recommended(recommended_ids, reviews):
        if len(recommended_ids):
            data_frame = db.get_recipes(recipe_ids=recommended_ids, columns=['id', 'name', 'description', 'img_url'])
            data_frame['rating'] = reviews[reviews.recipe_id.isin(recommended_ids)].groupby('recipe_id').rating.mean()[recommended_ids].fillna(0).values
            recommended_recipes = [{
                'id': x[0],
                'name': x[1],
                'desc': x[2],
                'img_url': x[3],
                'rating': range(int(np.round(x[4]))),
                'rating_null': range(5 - int(np.round(x[4])))
            } for x in data_frame.values]
            return recommended_recipes
        else:
            return []
