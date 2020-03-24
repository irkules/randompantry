from django.core.cache import cache
import numpy as np
import pandas as pd
from collections import defaultdict
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.decomposition import TruncatedSVD
from surprise import Dataset, KNNBaseline, Reader, SVD
from .models import Ingredient, Recipe, Review, Tag
from .nearest_recipes import NearestRecipes

# TODO: Needs refactoring

# Landing Page content helpers

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
def get_recommended(user_id = 1):
    reviews = get_reviews()
    if len(reviews) == 0:
        return []
    else:
        reviews = reviews[['user_id', 'recipe_id', 'rating']]
    
    if (reviews.user_id != user_id).all():
        return []
    else:
        predictions_cache_key = 'svd_predictions'
        if predictions_cache_key in cache:
            predictions = cache.get(predictions_cache_key)
        else:
            data = Dataset.load_from_df(reviews, Reader(rating_scale=(1, 5)))
            trainset = data.build_full_trainset()
            testset = trainset.build_anti_testset()
            # Train SVD
            model = SVD(random_state = 2019)
            model.fit(trainset)
            predictions = model.test(testset)
            cache.set(predictions_cache_key, predictions)
        # Get recommended recipes
        top_n = get_top_n(predictions, n = 15)
        rec_ids = np.array(top_n[user_id])[:, 0]
        recs = get_recipes(rec_ids)[['id', 'name', 'description', 'img_url']]
        # Add average ratings
        recs['rating'] = reviews[reviews.recipe_id.isin(rec_ids)].groupby('recipe_id').rating.mean()[rec_ids].fillna(0).values
        # Convert to django context format
        recs = [{'id': x[0], 'name': x[1], 'desc': x[2], 'img_url': x[3], 'rating': range(int(np.round(x[4]))), 'rating_null': range(5 - int(np.round(x[4])))} for x in recs.values]
        return recs

def clear_recommended_cache():
    cache.delete('svd_predictions')

# Favorites
def get_favourites(user_id = 1):
    # TODO: Needs implentation
    return []

# Make Again
def get_make_again(user_id = 1):
    reviews = get_reviews()
    if len(reviews) == 0:
        return []
    if (reviews.user_id != user_id).all():
        return []
    rec_ids = reviews[reviews.user_id == user_id].sort_values(by=['rating'], ascending=False)[:15].recipe_id.values
    recs = get_recipes(rec_ids)[['id', 'name', 'description', 'img_url']]
    recs['rating'] = reviews[reviews.recipe_id.isin(rec_ids)].groupby('recipe_id').rating.mean()[rec_ids].fillna(0).values
    recs = [{'id': x[0], 'name': x[1], 'desc': x[2], 'img_url': x[3], 'rating': range(int(np.round(x[4]))), 'rating_null': range(5 - int(np.round(x[4])))} for x in recs.values]
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
    recs['rating'] = rev.rating.values
    recs = [{'id': x[0], 'name': x[1], 'desc': x[2], 'img_url': x[3], 'rating': range(int(np.round(x[4]))), 'rating_null': range(5 - int(np.round(x[4])))} for x in recs.values]
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
    recs_1['rating'] = reviews[reviews.recipe_id.isin(recs_1.id)].groupby('recipe_id').rating.mean()[recs_1.id].fillna(0).values
    recs_2['rating'] = reviews[reviews.recipe_id.isin(recs_2.id)].groupby('recipe_id').rating.mean()[recs_2.id].fillna(0).values
    recs_3['rating'] = reviews[reviews.recipe_id.isin(recs_3.id)].groupby('recipe_id').rating.mean()[recs_3.id].fillna(0).values    
    recs_1 = [{'id': x[0], 'name': x[1], 'desc': x[2], 'img_url': x[3], 'rating': range(int(np.round(x[4]))), 'rating_null': range(5 - int(np.round(x[4])))} for x in recs_1.values]
    recs_2 = [{'id': x[0], 'name': x[1], 'desc': x[2], 'img_url': x[3], 'rating': range(int(np.round(x[4]))), 'rating_null': range(5 - int(np.round(x[4])))} for x in recs_2.values]
    recs_3 = [{'id': x[0], 'name': x[1], 'desc': x[2], 'img_url': x[3], 'rating': range(int(np.round(x[4]))), 'rating_null': range(5 - int(np.round(x[4])))} for x in recs_3.values]
    return recs_1, recs_2, recs_3

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

# TODO: Needs implementation
def get_nutr_pick():
    return []

# TODO: Recipe details page content helpers

def get_similar_rating(recipe_id):
    reviews = get_reviews()
    if len(reviews) == 0:
        return []
    if (reviews.recipe_id != recipe_id).all():
        return []
    KNNBaseline_cache_key = 'KNNBaseline'
    if KNNBaseline_cache_key in cache:
        model = cache.get(KNNBaseline_cache_key)
    else:
        reviews = reviews[['user_id', 'recipe_id', 'rating']]
        data = Dataset.load_from_df(reviews, Reader(rating_scale=(1, 5)))
        trainset = data.build_full_trainset()
        model = KNNBaseline(sim_options={'name': 'pearson_baseline', 'user_based': False}, verbose=False)
        model.fit(trainset)
        cache.set(KNNBaseline_cache_key, model)
    inner_id = model.trainset.to_inner_iid(recipe_id)
    nearest_recipe_inner_ids = model.get_neighbors(inner_id, k=15)
    nearest_recipe_ids = [model.trainset.to_raw_iid(id) for id in nearest_recipe_inner_ids]
    nearest_recipes = get_recipes(rec_ids=nearest_recipe_ids)[['id', 'name', 'description', 'img_url']]
    nearest_recipes['rating'] = reviews[reviews.recipe_id.isin(nearest_recipe_ids)].groupby('recipe_id').rating.mean()[nearest_recipe_ids].fillna(0).values
    nearest_recipes = [{'id': x[0], 'name': x[1], 'desc': x[2], 'img_url': x[3], 'rating': range(int(np.round(x[4]))), 'rating_null': range(5 - int(np.round(x[4])))} for x in nearest_recipes.values]
    return nearest_recipes

def get_similar_ingr(recipe_id):
    recipes = get_recipes()
    if len(recipes) == 0:
        return []
    NRIngr_cache_key = 'NRIngr'
    ingr_cache_key = 'ingr'
    if (NRIngr_cache_key in cache) and (ingr_cache_key in cache):
        model = cache.get(NRIngr_cache_key)
        ingredients = cache.get(ingr_cache_key)
    else:
        mlb = MultiLabelBinarizer(sparse_output = True)
        ingredients = mlb.fit_transform(recipes.ingredient_ids)
        tsvd = TruncatedSVD(n_components = 100, random_state = 2019)
        ingredients = tsvd.fit_transform(ingredients)
        cache.set(ingr_cache_key, ingredients)
        model = NearestRecipes(k = 16)
        model.fit(ingredients)
        cache.set(NRIngr_cache_key, model)
    nearest_recipe_ids = model.get_nearest_recipes(
        test = ingredients[recipes['id'] == recipe_id], 
        train_id = recipes['id'].values)[0][-15:]
    nearest_recipes = get_recipes(rec_ids=nearest_recipe_ids)[['id', 'name', 'description', 'img_url']]
    reviews = get_reviews()
    nearest_recipes['rating'] = reviews[reviews.recipe_id.isin(nearest_recipe_ids)].groupby('recipe_id').rating.mean()[nearest_recipe_ids].fillna(0).values
    nearest_recipes = [{'id': x[0], 'name': x[1], 'desc': x[2], 'img_url': x[3], 'rating': range(int(np.round(x[4]))), 'rating_null': range(5 - int(np.round(x[4])))} for x in nearest_recipes.values]
    return nearest_recipes

def get_similar_tags(recipe_id):
    recipes = get_recipes()
    if len(recipes) == 0:
        return []
    NRTags_cache_key = 'NRTags'
    tags_cache_key = 'tags'
    if (NRTags_cache_key in cache) and (tags_cache_key in cache):
        model = cache.get(NRTags_cache_key)
        tags = cache.get(tags_cache_key)
    else:
        mlb = MultiLabelBinarizer(sparse_output = True)
        tags = mlb.fit_transform(recipes.tag_ids)
        tsvd = TruncatedSVD(n_components = 100, random_state = 2019)
        tags = tsvd.fit_transform(tags)
        cache.set(tags_cache_key, tags)
        model = NearestRecipes(k = 16)
        model.fit(tags)
        cache.set(NRTags_cache_key, model)
    nearest_recipe_ids = model.get_nearest_recipes(
        test = tags[recipes['id'] == recipe_id], 
        train_id = recipes['id'].values)[0][-15:]
    nearest_recipes = get_recipes(rec_ids=nearest_recipe_ids)[['id', 'name', 'description', 'img_url']]
    reviews = get_reviews()
    nearest_recipes['rating'] = reviews[reviews.recipe_id.isin(nearest_recipe_ids)].groupby('recipe_id').rating.mean()[nearest_recipe_ids].fillna(0).values
    nearest_recipes = [{'id': x[0], 'name': x[1], 'desc': x[2], 'img_url': x[3], 'rating': range(int(np.round(x[4]))), 'rating_null': range(5 - int(np.round(x[4])))} for x in nearest_recipes.values]
    return nearest_recipes

def get_similar_nutr(recipe_id):
    recipes = get_recipes()
    if len(recipes) == 0:
        return []
    NRNutr_cache_key = 'NRNutr'
    if NRNutr_cache_key in cache:
        model = cache.get(NRNutr_cache_key)
    else:
        nutrition = recipes.nutrition.values.tolist()
        model = NearestRecipes(k = 16)
        model.fit(nutrition)
        cache.set(NRNutr_cache_key, model)
    nearest_recipe_ids = model.get_nearest_recipes(
        test = recipes.nutrition[recipes['id'] == recipe_id].tolist(), 
        train_id = recipes['id'].values)[0][-15:]
    nearest_recipes = get_recipes(rec_ids=nearest_recipe_ids)[['id', 'name', 'description', 'img_url']]
    reviews = get_reviews()
    nearest_recipes['rating'] = reviews[reviews.recipe_id.isin(nearest_recipe_ids)].groupby('recipe_id').rating.mean()[nearest_recipe_ids].fillna(0).values
    nearest_recipes = [{'id': x[0], 'name': x[1], 'desc': x[2], 'img_url': x[3], 'rating': range(int(np.round(x[4]))), 'rating_null': range(5 - int(np.round(x[4])))} for x in nearest_recipes.values]
    return nearest_recipes

def clear_similar_recipes_cache():
    cache.delete('KNNBaseline')
    cache.delete('NRIngr')
    cache.delete('ingr')
    cache.delete('NRTags')
    cache.delete('tags')
    cache.delete('NRNutr')
