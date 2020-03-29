from blog import db, tasks
from blog.models import Recipe
from blog.nearest_recipes import NearestRecipes, NearestRecipesBaseline
from blog.recommender import RecipeRecommender
from blog.redis import RECOMMENDED_KEY, FAVOURITES_KEY, MAKE_AGAIN_KEY, TOP_RATED_KEY
from django.core.cache import cache
from numpy import logical_and
from randompantry.settings import USE_CELERY
from statistics import mean


class Content:
    @staticmethod
    def get_recipes(ids, reviews, all_columns=False):
        if all_columns:
            recipes = db.get_recipes(recipe_ids=ids)
        else:
            recipes = db.get_recipes(recipe_ids=ids, columns=['id', 'name', 'description', 'img_url', 'rating'])
        for recipe in recipes:
            current_rating = round(recipe['rating'])
            recipe['rating'] = range(current_rating)
            recipe['rating_null'] = range(5 - current_rating)
        return recipes

class HomeContent(Content):
    @staticmethod
    def get_home_context():
        home = dict()
        reviews = db.get_reviews(columns=['user_id', 'recipe_id', 'rating'])
        if len(reviews):
            home['top_rated'] = HomeContent.get_top_rated(reviews)
            if (reviews['user_id'] == 1).any():
                home['recommended'] = HomeContent.get_recommended(reviews)
                home['make_again'] = HomeContent.get_make_again(reviews)
        return home

    @staticmethod
    def get_recommended(reviews):
        if RECOMMENDED_KEY in cache:
            recommended_ids = cache.get(RECOMMENDED_KEY)
        else:
            db_cache = db.get_home_cache(columns=['recommended'])
            if 'recommended' in db_cache:
                recommended_ids = db_cache['recommended']
                if recommended_ids == [-1] or recommended_ids is None: # If cache was previously purged
                    recommended_ids = tasks.get_recommended_ids(reviews)
                    db.update_home_cache(columns=['recommended'], values=[recommended_ids])
                cache.set(RECOMMENDED_KEY, recommended_ids)
            else:
                recommended_ids = tasks.get_recommended_ids(reviews)
                cache.set(RECOMMENDED_KEY, recommended_ids)
                db.update_home_cache(columns=['recommended'], values=[recommended_ids])
        return HomeContent.get_recipes(recommended_ids, reviews)

    @staticmethod
    def get_make_again(reviews):
        if MAKE_AGAIN_KEY in cache:
            make_again_ids = cache.get(MAKE_AGAIN_KEY)
        else:
            db_cache = db.get_home_cache(columns=['make_again'])
            if 'make_again' in db_cache:
                make_again_ids = db_cache['make_again']
                if make_again_ids == [-1] or make_again_ids is None: # If cache was previously purged
                    make_again_ids = tasks.get_make_again_ids(reviews)
                    db.update_home_cache(columns=['make_again'], values=[make_again_ids])
                cache.set(MAKE_AGAIN_KEY, make_again_ids)
            else:
                make_again_ids = tasks.get_make_again_ids(reviews)
                cache.set(MAKE_AGAIN_KEY, make_again_ids)
                db.update_home_cache(columns=['make_again'], values=[make_again_ids])
        return RecipeDetailContent.get_recipes(make_again_ids, reviews)

    @staticmethod
    def get_top_rated(reviews):
        if TOP_RATED_KEY in cache:
            top_rated_ids = cache.get(TOP_RATED_KEY)
        else:
            db_cache = db.get_home_cache(columns=['top_rated'])
            if 'top_rated' in db_cache:
                top_rated_ids = db_cache['top_rated']
                if top_rated_ids == [-1] or top_rated_ids is None: # If cache was previously purged
                    top_rated_ids = tasks.get_top_rated_ids(reviews)
                    db.update_home_cache(columns=['top_rated'], values=[top_rated_ids])
                cache.set(TOP_RATED_KEY, top_rated_ids)
            else:
                top_rated_ids = tasks.get_top_rated_ids(reviews)
                cache.set(TOP_RATED_KEY, top_rated_ids)
                db.update_home_cache(columns=['top_rated'], values=[top_rated_ids])
        return RecipeDetailContent.get_recipes(top_rated_ids, reviews)

class RecipeDetailContent(Content):
    @staticmethod
    def get_recipe_detail_context(recipe_id):
        reviews = db.get_reviews(columns=['user_id', 'recipe_id', 'rating'])
        recipes = RecipeDetailContent.get_recipes([], reviews, all_columns=True)
        # Current Recipe Attributes
        matched_recipes = [recipe for recipe in recipes if recipe['id'] == recipe_id]
        if not matched_recipes:
            return None
        current_recipe = matched_recipes[0]
        current_recipe['description'] = current_recipe['description'].capitalize()
        current_recipe['has_rated'] = len(reviews[logical_and(reviews.user_id == 1, reviews.recipe_id == recipe_id)]) != 0
        ingredients = db.get_ingredients(ingredient_ids=current_recipe['ingredient_ids'])
        current_recipe['ingredients'] = [ingredient.capitalize() for ingredient in ingredients]
        current_recipe['tags'] = db.get_tags(tag_ids=current_recipe['tag_ids'])
        steps = []
        for step in current_recipe['steps']:
            if step[0] == "'":
                step = step[1:]
            if step[-1] == "'":
                step = step[:-1]
            steps.append(step.capitalize())
        current_recipe['steps'] = steps
        # Similar Recipes
        similar_rating_ids = current_recipe['similar_rating']
        similar_ingredient_ids = current_recipe['similar_ingredients']
        similar_tag_ids = current_recipe['similar_tags']
        similar_nutrition_ids = current_recipe['similar_nutrition']
        has_cached_ids = similar_rating_ids and similar_ingredient_ids and similar_tag_ids and similar_nutrition_ids
        if not has_cached_ids:
            similar_rating_ids = RecipeDetailContent.get_similar_rating_ids(recipe_id, reviews)
            similar_ingredient_ids = RecipeDetailContent.get_similar_ingredients_ids(recipe_id, recipes, reviews)
            similar_tag_ids = RecipeDetailContent.get_similar_tags_ids(recipe_id, recipes, reviews)
            similar_nutrition_ids = RecipeDetailContent.get_similar_nutrition_ids(recipe_id, recipes, reviews)
            db.update_recipe_cache(
                recipe_id=recipe_id,
                columns=['similar_rating', 'similar_ingredients', 'similar_tags', 'similar_nutrition'],
                values=[similar_rating_ids, similar_ingredient_ids, similar_tag_ids, similar_rating_ids]
            )
        current_recipe['similar_rating'] = RecipeDetailContent.get_recipes(similar_rating_ids, reviews)
        current_recipe['similar_ingredients'] = RecipeDetailContent.get_recipes(similar_ingredient_ids, reviews)
        current_recipe['similar_tags'] = RecipeDetailContent.get_recipes(similar_tag_ids, reviews)
        current_recipe['similar_nutrition'] = RecipeDetailContent.get_recipes(similar_nutrition_ids, reviews)
        return current_recipe

    @staticmethod
    def get_recipe_rating(recipe_id, reviews):
        reviews = reviews[reviews.recipe_id == recipe_id]
        if len(reviews):
            mean_rating = round(mean(reviews.rating))
            rating = range(mean_rating)
            rating_null = range(5 - mean_rating)
            return rating, rating_null
        return [], []

    @staticmethod
    def get_similar_rating_ids(recipe_id, reviews):
        if (reviews.recipe_id != recipe_id).all():
            return []
        model = NearestRecipesBaseline(k=40)
        model.fit(reviews)
        return model.predict(recipe_id)

    @staticmethod
    def get_similar_ingredients_ids(recipe_id, recipes):
        model = NearestRecipes()
        ingredient_ids_list = [recipe['ingredient_ids'] for recipe in recipes]
        model.fit(ingredient_ids_list)
        return model.predict(recipe_id, recipes.id)

    @staticmethod
    def get_similar_tags_ids(recipe_id, recipes):
        model = NearestRecipes()
        tag_ids_list = [recipe['tag_ids'] for recipe in recipes]
        model.fit(tag_ids_list)
        return model.predict(recipe_id, recipes.id)

    @staticmethod
    def get_similar_nutrition_ids(recipe_id, recipes):
        model = NearestRecipes(reduce=False)
        nutrition_list = [recipe['nutrition'] for recipe in recipes]
        model.fit(nutrition_list)
        return model.predict(recipe_id, recipes.id)

    @staticmethod
    def add_review(rating, review, recipe_id, user_id):
        cache.delete_many([RECOMMENDED_KEY, MAKE_AGAIN_KEY, TOP_RATED_KEY])
        if USE_CELERY:
            tasks.insert_review.delay(rating, review, recipe_id, user_id)
        else:
            tasks.insert_review(rating, review, recipe_id, user_id)
