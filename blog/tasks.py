from __future__ import absolute_import, unicode_literals

from blog import db
from blog.nearest_recipes import NearestRecipes, NearestRecipesBaseline
from blog.recommender import RecipeRecommender
from celery import shared_task
from celery.signals import worker_ready


@worker_ready.connect
def app_startup_tasks(*args, **kwargs):
    refresh_home_content()

@shared_task
def refresh_home_content():
    reviews = db.get_reviews(columns=['user_id', 'recipe_id', 'rating'])
    recommended_ids = get_recommended_ids(reviews)
    db.update_home_cache(columns=['recommended'], values=[recommended_ids])
    db.get_make_again(columns=['id'], update_only=True)
    db.get_top_rated(columns=['id'], update_only=True)
    return None

@shared_task
def get_recommended_ids(reviews):
    recommender = RecipeRecommender()
    recommender.fit(reviews)
    recommended_ids = recommender.predict(reviews)
    return recommended_ids

@shared_task
def insert_review(rating, review, recipe_id, user_id):
    db.insert_review(rating, review, recipe_id, user_id)
    refresh_home_content()

# @shared_task
# def train_SVDpp_model(params):
#     reviews = db.get_reviews(columns=['user_id', 'recipe_id', 'rating'])
#     recommended_ids = get_recommended_ids(reviews)
#     db.update_home_cache(columns=['recommended'], values=[recommended_ids])
#     return None

# @shared_task
# def train_KNN_model(params):
#     recipes = db.get_recipes()
#     recipe_ids = recipes.id
#     reviews = db.get_reviews(columns=['user_id', 'recipe_id', 'rating'])
#     # Instantiate models
#     nrb = NearestRecipesBaseline(k=40)
#     nr = NearestRecipes()
#     nrf = NearestRecipes(reduce=False)
#     # Cache nearest recipe ids
#     for recipe_id in recipe_ids:
#         # Rating
#         nrb.fit(reviews)
#         similar_rating_ids = nrb.predict(recipe_id)
#         # Ingredients
#         nr.fit(recipes['ingredient_ids'])
#         similar_ingredient_ids = nr.predict(recipe_id, recipe_ids)
#         # Tags
#         nr.fit(recipes['tag_ids'])
#         similar_tag_ids = nr.predict(recipe_id, recipe_ids)
#         # Nutrition
#         nrf.fit(recipes['nutrition'])
#         similar_nutrition_ids = nrf.predict(recipe_id, recipe_ids)
#         # Cache ids in db
#         db.update_recipe_cache(
#             recipe_id=recipe_id,
#             columns=['similar_rating', 'similar_ingredients', 'similar_tags', 'similar_nutrition'],
#             values=[similar_rating_ids, similar_ingredient_ids, similar_tag_ids, similar_nutrition_ids]
#         )
#     return None
