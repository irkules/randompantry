from collections import defaultdict
from surprise import Dataset, Reader, SVD, SVDpp


class RecipeRecommender:
    def __init__(self, n_factors=20, n_epochs=20, lr_all=0.007, reg_all=0.02):
        # self.model = SVDpp(n_factors=n_factors, n_epochs=n_epochs, lr_all=lr_all, reg_all=reg_all, random_state=2020)
        self.model = SVD(random_state=2020)

    def fit(self, reviews):
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(reviews, reader)
        self.trainset = data.build_full_trainset()
        self.testset = self.trainset.build_anti_testset()
        return self.model.fit(self.trainset)

    def predict(self, reviews, n=20):
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
