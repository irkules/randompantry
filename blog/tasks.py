from __future__ import absolute_import, unicode_literals

from blog import db
from blog.modeling import RecipeRecommender, RecipeNet
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
    recommended_ids = recommender.predict()
    return recommended_ids

@shared_task
def insert_review(rating, recipe_id, user_id):
    db.insert_review(rating, recipe_id, user_id)
    refresh_home_content()
