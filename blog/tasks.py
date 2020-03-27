from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery.signals import worker_ready
from blog import db
from blog.nearest_recipes import NearestRecipes, NearestRecipesBaseline
from blog.recommender import RecipeRecommender
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


# @shared_task
# # @worker_ready.connect
# def update_recommended(**kwargs):
#     reviews = db.get_reviews(columns=['user_id', 'recipe_id', 'rating'])
#     recommender = RecipeRecommender()
#     recommender.fit(reviews)
#     recommended_ids = recommender.predict(reviews)
#     db.update_home_cache(columns=['recommended'], values=[recommended_ids])
#     return None

# @shared_task
# # @worker_ready.connect
# def update_similar_recipes(**kwargs):
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
#         nr.fit(recipes.ingredient_ids)
#         similar_ingredient_ids = nr.predict(recipe_id, recipe_ids)
#         # Tags
#         nr.fit(recipes.tag_ids)
#         similar_tag_ids = nr.predict(recipe_id, recipe_ids)
#         # Nutrition
#         nrf.fit(recipes.nutrition)
#         similar_nutrition_ids = nrf.predict(recipe_id, recipe_ids)
#         # Cache ids in db
#         db.update_recipe_cache(
#             recipe_id=recipe_id,
#             columns=['similar_rating', 'similar_ingredients', 'similar_tags', 'similar_nutrition'],
#             values=[similar_rating_ids, similar_ingredient_ids, similar_tag_ids, similar_nutrition_ids]
#         )
#     return None

# @shared_task
# def update_home_cache(columns, values):
#     status = db.update_home_cache(columns=columns, values=values)
#     logger.info('status update:', status)
#     return None

# @shared_task
# def update_recipe_cache(recipe_id, columns, values):
#     db.update_recipe_cache(recipe_id=recipe_id, columns=columns, values=values)
#     return None

# TODO: Implement this!
# @shared_task
# def update_favourites(**kwargs):
#     return None

# @shared_task
# def update_make_again(**kwargs):
#     reviews = db.get_reviews(columns=['user_id', 'recipe_id', 'rating'])
#     if len(reviews) != 0 and (reviews.user_id == 1).any():
#         recipe_ids = list(reviews[reviews.user_id == 1].sort_values(by=['rating'], ascending=False).recipe_id.values[:20])
#         db.update_home_cache(columns=['make_again'], values=[recipe_ids])
#     return None
