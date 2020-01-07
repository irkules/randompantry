import numpy as np
import pandas as pd
from collections import defaultdict
from surprise import Dataset
from surprise import Reader
from surprise import SVD
from .models import Ingredient, Recipe, Review, Tag

# TODO: All content delivery functions need improvements

def get_reviews():
    df = pd.DataFrame(list(Review.objects.all().values()))
    if len(df) != 0:
        df.index = df['id'].values
    return df

def get_recipes(rec_ids=None):
    if rec_ids is not None:
        querySet = Recipe.objects.filter(pk__in=rec_ids)
    else:
        querySet = Recipe.objects.all()
    df = pd.DataFrame(list(querySet.values()))
    if len(df) != 0:
        df.index = df['id'].values
    if rec_ids is not None:
        df = df.loc[rec_ids].reset_index(drop=True)
    return df

def get_top_n(predictions, n):
    top_n = defaultdict(list)
    for uid, iid, _, est, _ in predictions:
        top_n[uid].append((iid, est))
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]
    return top_n

# Recommended
def get_recommended(user_id):
    reviews = get_reviews()
    if len(reviews) == 0:
        return []
    else:
        reviews = reviews[['user_id', 'recipe_id', 'rating']]
    if (reviews.user_id != user_id).all():
        return []
    else:
        data = Dataset.load_from_df(reviews, Reader(rating_scale=(1, 5)))
        trainset = data.build_full_trainset()
        testset = trainset.build_anti_testset()
        # Train SVD
        model = SVD(random_state = 2019, verbose = True)
        model.fit(trainset)
        predictions = model.test(testset)
        top_n = get_top_n(predictions, n = 15)
        # Get recommended recipes
        rec_ids = np.array(top_n[user_id])[:, 0]
        recs = get_recipes(rec_ids)[['id', 'name', 'description', 'img_url']]
        # Add average ratings
        recs['rating'] = reviews[reviews.recipe_id.isin(rec_ids)].groupby('recipe_id').rating.mean()[rec_ids].values
        # Convert to django context format
        recs = [{'id': x[0], 'name': x[1], 'desc': x[2], 'img_url': x[3], 'rating': x[4]} for x in recs.values]
        return recs

# Favorites
def get_favourites(user_id):
    # TODO: Needs implentation
    return []

# Make Again
def get_make_again(user_id):
    reviews = get_reviews()
    if len(reviews) == 0:
        return []
    if (reviews.user_id != user_id).all():
        return []
    rec_ids = reviews[reviews.user_id == user_id].sort_values(by=['rating'], ascending=False)[:15].recipe_id.values
    recs = get_recipes(rec_ids)[['id', 'name', 'description', 'img_url']]
    recs['img_url'] = 'https://images.pexels.com/photos/574114/pexels-photo-574114.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940'
    recs['rating'] = reviews[reviews.recipe_id.isin(rec_ids)].groupby('recipe_id').rating.mean()[rec_ids].values
    recs = [{'id': x[0], 'name': x[1], 'desc': x[2], 'img_url': x[3], 'rating': x[4]} for x in recs.values]
    return recs

# Top Rated
def get_top_rated():
    reviews = get_reviews()
    if len(reviews) == 0:
        return []
    rev = reviews.groupby('recipe_id')[['rating', 'recipe_id']].mean().reset_index(drop=True)
    rev['count'] = reviews.groupby('recipe_id').rating.count().values
    rev = rev.sort_values(by=['rating', 'count'],ascending=[False, False])[:15]
    rec_ids = rev.recipe_id.values
    recs = get_recipes(rec_ids)[['id', 'name', 'description', 'img_url']]
    recs['img_url'] = 'https://images.pexels.com/photos/574114/pexels-photo-574114.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940'
    recs['rating'] = rev.rating.values
    recs = [{'id': x[0], 'name': x[1], 'desc': x[2], 'img_url': x[3], 'rating': x[4]} for x in recs.values]
    return recs

# Top Tags
def get_top_tags():
    recs = get_recipes()
    if len(recs) == 0:
        return [], [], []
    recs_explode = recs.explode('tag_ids')
    top_tag_ids = recs_explode.groupby('tag_ids')['id'].count().sort_values(ascending=False)[:3].index.values
    recs_1 = recs_explode[recs_explode.tag_ids == top_tag_ids[0]].sample(n=15)[['id', 'name', 'description', 'img_url']]
    recs_2 = recs_explode[recs_explode.tag_ids == top_tag_ids[1]].sample(n=15)[['id', 'name', 'description', 'img_url']]
    recs_3 = recs_explode[recs_explode.tag_ids == top_tag_ids[2]].sample(n=15)[['id', 'name', 'description', 'img_url']]
    reviews = get_reviews()
    recs_1['rating'] = reviews[reviews.recipe_id.isin(recs_1.id)].groupby('recipe_id').rating.mean()[recs_1.id].values
    recs_2['rating'] = reviews[reviews.recipe_id.isin(recs_2.id)].groupby('recipe_id').rating.mean()[recs_2.id].values
    recs_3['rating'] = reviews[reviews.recipe_id.isin(recs_3.id)].groupby('recipe_id').rating.mean()[recs_3.id].values    
    recs_1 = [{'id': x[0], 'name': x[1], 'desc': x[2], 'img_url': x[3], 'rating': x[4]} for x in recs_1.values]
    recs_2 = [{'id': x[0], 'name': x[1], 'desc': x[2], 'img_url': x[3], 'rating': x[4]} for x in recs_2.values]
    recs_3 = [{'id': x[0], 'name': x[1], 'desc': x[2], 'img_url': x[3], 'rating': x[4]} for x in recs_3.values]
    return recs_1, recs_2, recs_3

def get_nutr_pick():
    # TODO: Needs implementation
    return []

def get_ingr(ingr_ids = None):
    if ingr_ids is None:
        querySet = Ingredient.objects.all()
    else:
        querySet = Ingredient.objects.filter(pk__in=ingr_ids)
    df = pd.DataFrame(list(querySet.values()))
    df.index = df['id'].values
    if ingr_ids is not None:
        df = df.loc[ingr_ids].reset_index(drop = True)
    return df.name.values

def get_tags(tag_ids = None):
    if tag_ids is None:
        querySet = Tag.objects.all()
    else:
        querySet = Tag.objects.filter(pk__in=tag_ids)
    df = pd.DataFrame(list(querySet.values()))
    df.index = df['id'].values
    if tag_ids is not None:
        df = df.loc[tag_ids].reset_index(drop=True)
    return df.name.values
