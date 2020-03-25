from django.core.cache import cache
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.decomposition import TruncatedSVD
from surprise import Dataset, KNNBaseline, Reader
from blog import db, redis
from blog.models import Recipe
from blog.nearest_recipes import NearestRecipes, NearestRecipesBaseline
from blog.recommender import RecipeRecommender


class HomeContent:
    @staticmethod
    def get_home_context():
        reviews = db.get_reviews(columns=['user_id', 'recipe_id', 'rating'])
        recommended = HomeContent.get_recommended(reviews)
        favourites = HomeContent.get_favourites()
        make_again = HomeContent.get_make_again(reviews)
        top_rated = HomeContent.get_top_rated(reviews)
        return recommended, favourites, make_again, top_rated

    @staticmethod
    def get_recommended(reviews):
        if len(reviews) == 0 or (reviews.user_id != 1).all():
            return []
        if redis.RECOMMENDED_KEY in cache:
            recommended_ids = cache.get(redis.RECOMMENDED_KEY)
        else:
            db_cache = db.get_home_cache(columns=['recommended'])
            if 'recommended' in db_cache:
                recommended_ids = db_cache['recommended']
                if recommended_ids == [-1] or recommended_ids is None: # If cache was previously purged
                    recommended_ids = HomeContent.get_recommended_ids(reviews)
                    db.update_home_cache(columns=['recommended'], values=[recommended_ids])
                cache.set(redis.RECOMMENDED_KEY, recommended_ids)
            else:
                recommended_ids = HomeContent.get_recommended_ids(reviews)
                cache.set(redis.RECOMMENDED_KEY, recommended_ids)
                db.update_home_cache(columns=['recommended'], values=[recommended_ids])
        recommended = HomeContent.get_recommended_recipes(recommended_ids, reviews)
        return recommended

    @staticmethod
    def get_recommended_ids(reviews):
        recommender = RecipeRecommender()
        recommender.fit(reviews)
        recommended_ids = recommender.predict(reviews)
        return recommended_ids

    @staticmethod
    def get_recommended_recipes(recommended_ids, reviews):
        if len(recommended_ids):
            recipes = db.get_recipes(recipe_ids=recommended_ids, columns=['id', 'name', 'description', 'img_url', 'rating'])
            return [{
                'id': x[0],
                'name': x[1],
                'desc': x[2],
                'img_url': x[3],
                'rating': range(int(np.round(x[4]))),
                'rating_null': range(5 - int(np.round(x[4])))
            } for x in recipes.values]
        else:
            return []

    @staticmethod
    def purge_home_cache():
        cache.delete(redis.RECOMMENDED_KEY)
        cache.delete(redis.MAKE_AGAIN_KEY)
        cache.delete(redis.TOP_RATED_KEY)
        db.update_home_cache(columns=['recommended', 'make_again', 'top_rated'], values=[[-1], [-1], [-1]])

    # TODO: Implentation this!
    @staticmethod
    def get_favourites():
        return []

    @staticmethod
    def get_make_again(reviews):
        if len(reviews) == 0 or (reviews.user_id != 1).all():
            return [] 
        if redis.MAKE_AGAIN_KEY in cache:
            make_again_ids = cache.get(redis.MAKE_AGAIN_KEY)
        else:
            db_cache = db.get_home_cache(columns=['make_again'])
            if 'make_again' in db_cache:
                make_again_ids = db_cache['make_again']
                if make_again_ids == [-1] or make_again_ids is None: # If cache was previously purged
                    make_again_ids = HomeContent.get_make_again_ids(reviews)
                    db.update_home_cache(columns=['make_again'], values=[make_again_ids])
                cache.set(redis.MAKE_AGAIN_KEY, make_again_ids)
            else:
                make_again_ids = HomeContent.get_make_again_ids(reviews)
                cache.set(redis.MAKE_AGAIN_KEY, make_again_ids)
                db.update_home_cache(columns=['make_again'], values=[make_again_ids])
        return RecipeDetailContent.get_recipes(make_again_ids, reviews)

    @staticmethod
    def get_make_again_ids(reviews):
        user_reviews = reviews[reviews.user_id == 1]
        sorted_reviews = user_reviews.sort_values(by=['rating'], ascending=False)
        return list(sorted_reviews.recipe_id.values[:20])

    @staticmethod
    def get_top_rated(reviews):
        if len(reviews) == 0 or (reviews.user_id != 1).all():
            return [] 
        if redis.TOP_RATED_KEY in cache:
            top_rated_ids = cache.get(redis.TOP_RATED_KEY)
        else:
            db_cache = db.get_home_cache(columns=['top_rated'])
            if 'top_rated' in db_cache:
                top_rated_ids = db_cache['top_rated']
                if top_rated_ids == [-1] or top_rated_ids is None: # If cache was previously purged
                    top_rated_ids = HomeContent.get_top_rated_ids(reviews)
                    db.update_home_cache(columns=['top_rated'], values=[top_rated_ids])
                cache.set(redis.TOP_RATED_KEY, top_rated_ids)
            else:
                top_rated_ids = HomeContent.get_top_rated_ids(reviews)
                cache.set(redis.TOP_RATED_KEY, top_rated_ids)
                db.update_home_cache(columns=['top_rated'], values=[top_rated_ids])
        return RecipeDetailContent.get_recipes(top_rated_ids, reviews)

    @staticmethod
    def get_top_rated_ids(reviews):
        reviews = reviews.groupby('recipe_id')[['rating', 'recipe_id']].mean().reset_index(drop=True)
        reviews['count'] = reviews.groupby('recipe_id').rating.count().values
        sorted_reviews = reviews.sort_values(by=['rating', 'count'], ascending=[False, False])
        return list(sorted_reviews.recipe_id.values[:20])

class RecipeDetailContent:
    @staticmethod
    def get_recipe_detail_context(recipe_id):
        # TODO: recipe = recipes[recipes.id == recipe_id]
        current_recipe = Recipe.objects.get(id=recipe_id)
        recipes = db.get_recipes()
        reviews = db.get_reviews(columns=['user_id', 'recipe_id', 'rating'])
        rating, rating_null = RecipeDetailContent.get_recipe_rating(recipe_id, reviews)
        ingredients = db.get_ingredients(current_recipe.ingredient_ids).name
        tags = db.get_tags(current_recipe.tag_ids).name
        has_rated = len(reviews[np.logical_and(reviews.user_id == 1, reviews.recipe_id == recipe_id)]) != 0
        # Check db cache
        has_db_cache = current_recipe.similar_rating and current_recipe.similar_ingredients and current_recipe.similar_tags and current_recipe.similar_nutrition
        if has_db_cache:
            similar_rating = RecipeDetailContent.get_recipes(current_recipe.similar_rating, reviews)
            similar_ingredients = RecipeDetailContent.get_recipes(current_recipe.similar_ingredients, reviews)
            similar_tags = RecipeDetailContent.get_recipes(current_recipe.similar_tags, reviews)
            similar_nutrition = RecipeDetailContent.get_recipes(current_recipe.similar_nutrition, reviews)
        else:
            similar_rating = RecipeDetailContent.get_similar_rating(recipe_id, reviews)
            similar_ingredients = RecipeDetailContent.get_similar_ingredients(recipe_id, recipes, reviews)
            similar_tags = RecipeDetailContent.get_similar_tags(recipe_id, recipes, reviews)
            similar_nutrition = RecipeDetailContent.get_similar_nutrition(recipe_id, recipes, reviews)
            db.update_recipe_cache(
                recipe_id=recipe_id,
                columns=['similar_rating', 'similar_ingredients', 'similar_tags', 'similar_nutrition'],
                values=[
                    [x['id'] for x in similar_rating],
                    [x['id'] for x in similar_ingredients],
                    [x['id'] for x in similar_tags],
                    [x['id'] for x in similar_rating]
                ]
            )
        return current_recipe, rating, rating_null, ingredients, tags, has_rated, similar_rating, similar_ingredients, similar_tags, similar_nutrition

    @staticmethod
    def get_recipe_rating(recipe_id, reviews):
        current_recipe_review = reviews[reviews.recipe_id == recipe_id]
        if len(current_recipe_review):
            mean_rating = int(np.round(current_recipe_review.rating.mean()))
            rating = range(mean_rating)
            rating_null = range(5 - mean_rating)
        else:
            rating = []
            rating_null = []
        return rating, rating_null

    @staticmethod
    def get_similar_rating(recipe_id, reviews):
        if len(reviews) == 0 or (reviews.recipe_id != recipe_id).all():
            return []
        model = NearestRecipesBaseline(k=40)
        model.fit(reviews)
        nearest_recipe_ids = model.predict(recipe_id)
        return RecipeDetailContent.get_recipes(nearest_recipe_ids, reviews)

    @staticmethod
    def get_similar_ingredients(recipe_id, recipes, reviews):
        if len(recipes) == 0:
            return []
        model = NearestRecipes()
        model.fit(recipes.ingredient_ids)
        nearest_recipe_ids = model.predict(recipe_id, recipes.id)
        return RecipeDetailContent.get_recipes(nearest_recipe_ids, reviews)

    @staticmethod
    def get_similar_tags(recipe_id, recipes, reviews):
        if len(recipes) == 0:
            return []
        model = NearestRecipes()
        model.fit(recipes.tag_ids)
        nearest_recipe_ids = model.predict(recipe_id, recipes.id)
        return RecipeDetailContent.get_recipes(nearest_recipe_ids, reviews)

    @staticmethod
    def get_similar_nutrition(recipe_id, recipes, reviews):
        if len(recipes) == 0:
            return []
        model = NearestRecipes(reduce=False)
        model.fit(recipes.nutrition)
        nearest_recipe_ids = model.predict(recipe_id, recipes.id)
        return RecipeDetailContent.get_recipes(nearest_recipe_ids, reviews)

    @staticmethod
    def get_recipes(recipe_ids, reviews):
        recipes = db.get_recipes(recipe_ids=recipe_ids, columns=['id', 'name', 'description', 'img_url', 'rating'])
        return [{
            'id': x[0],
            'name': x[1],
            'desc': x[2],
            'img_url': x[3],
            'rating': range(int(np.round(x[4]))),
            'rating_null': range(5 - int(np.round(x[4])))
        } for x in recipes.values]

    # TODO: Implement this!
    @staticmethod
    def purge_similar_cache():
        return None
