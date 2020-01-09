from sklearn.neighbors import NearestNeighbors

class NearestRecipes:
    def __init__(self, k = 5):
        self.k = k
        self.neigh = None

    def fit(self, train):
        self.neigh = NearestNeighbors(self.k).fit(train)
        return self

    def get_nearest_recipes(self, test, train_id):
        if self.neigh is None:
            return None
        nearest_indices = self.neigh.kneighbors(test, return_distance = False)
        recipe_ids = [train_id[x] for x in nearest_indices]
        return recipe_ids
