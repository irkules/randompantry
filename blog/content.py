from django.core.cache import cache
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.decomposition import TruncatedSVD
from surprise import Dataset, KNNBaseline, Reader
from blog import db
from blog.models import Recipe
from blog.nearest_recipes import NearestRecipes
from blog.recommender import RecipeRecommender

def get_home_context():
    reviews = db.get_reviews(columns=['user_id', 'recipe_id', 'rating'])
    recommended = get_recommended(reviews)
    favourites = get_favourites()
    make_again = get_make_again(reviews)
    top_rated = get_top_rated(reviews)
    return recommended, favourites, make_again, top_rated

def get_recommended(reviews):
    if len(reviews) == 0 or (reviews.user_id != 1).all():
        return []
    recommender = RecipeRecommender()
    predictions_cache_key = 'svd_predictions'
    if predictions_cache_key in cache:
        predictions = cache.get(predictions_cache_key)
    else:
        recommender.fit(reviews)
        predictions = recommender.predict()
        cache.set(predictions_cache_key, predictions)
    recommended_ids = recommender.get_recommended_ids(predictions, reviews)
    recommended = recommender.get_recommended(recommended_ids)
    return recommended

def clear_recommended_cache():
    cache.delete('svd_predictions')

# TODO: Implentation this!
def get_favourites():
    return []

def get_make_again(reviews):
    if len(reviews) == 0 or (reviews.user_id != 1).all():
        return []
    recipe_ids = reviews[reviews.user_id == 1].sort_values(by=['rating'], ascending=False)[:15].recipe_id.values
    make_again = db.get_recipes(recipe_ids=recipe_ids, columns=['id', 'name', 'description', 'img_url'])
    make_again['rating'] = reviews[reviews.recipe_id.isin(recipe_ids)].groupby('recipe_id').rating.mean()[recipe_ids].fillna(0).values
    make_again = [{
        'id': x[0], 
        'name': x[1],
        'desc': x[2],
        'img_url': x[3],
        'rating': range(int(np.round(x[4]))),
        'rating_null': range(5 - int(np.round(x[4])))
    } for x in make_again.values]
    return make_again

def get_top_rated(reviews):
    if len(reviews) == 0:
        return []
    reviews = reviews.groupby('recipe_id')[['rating', 'recipe_id']].mean().reset_index(drop=True)
    reviews['count'] = reviews.groupby('recipe_id').rating.count().values
    reviews = reviews.sort_values(by=['rating', 'count'], ascending=[False, False])[:15]
    recipe_ids = reviews.recipe_id.values
    top_rated = db.get_recipes(recipe_ids=recipe_ids, columns=['id', 'name', 'description', 'img_url'])
    top_rated['rating'] = reviews.rating.values
    top_rated = [{
        'id': x[0],
        'name': x[1],
        'desc': x[2],
        'img_url': x[3],
        'rating': range(int(np.round(x[4]))),
        'rating_null': range(5 - int(np.round(x[4])))
    } for x in top_rated.values]
    return top_rated

def get_recipe_detail_context(recipe_id):
    recipes = db.get_recipes()
    # TODO: recipe = recipes[recipes.id == recipe_id]
    recipe = Recipe.objects.get(id=recipe_id)
    reviews = db.get_reviews()
    current_recipe_review = reviews[reviews.recipe_id == recipe_id]
    if len(current_recipe_review):
        mean_rating = int(np.round(current_recipe_review.rating.mean()))
        rating = range(mean_rating)
        rating_null = range(5 - mean_rating)
    else:
        rating = []
        rating_null = []
    ingredients = db.get_ingredients(recipe.ingredient_ids).name
    tags = db.get_tags(recipe.tag_ids).name
    has_rated = len(reviews[np.logical_and(reviews.user_id == 1, reviews.recipe_id == recipe_id)]) != 0
    similar_rating = get_similar_rating(recipe_id, reviews)
    similar_ingredients = get_similar_ingredients(recipe_id, recipes)
    similar_tags = get_similar_tags(recipe_id, recipes)
    similar_nutrition = get_similar_nutrition(recipe_id, recipes)
    return recipe, rating, rating_null, ingredients, tags, has_rated, similar_rating, similar_ingredients, similar_tags, similar_nutrition

def get_similar_rating(recipe_id, reviews):
    if len(reviews) == 0 or (reviews.recipe_id != recipe_id).all():
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
    nearest_recipes = db.get_recipes(recipe_ids=nearest_recipe_ids, columns=['id', 'name', 'description', 'img_url'])
    nearest_recipes['rating'] = reviews[reviews.recipe_id.isin(nearest_recipe_ids)].groupby('recipe_id').rating.mean()[nearest_recipe_ids].fillna(0).values
    nearest_recipes = [{
        'id': x[0],
        'name': x[1],
        'desc': x[2],
        'img_url': x[3],
        'rating': range(int(np.round(x[4]))),
        'rating_null': range(5 - int(np.round(x[4])))
    } for x in nearest_recipes.values]
    return nearest_recipes

def get_similar_ingredients(recipe_id, recipes):
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
        train_id = recipes['id'].values
    )[0][-15:]
    nearest_recipes = db.get_recipes(recipe_ids=nearest_recipe_ids, columns=['id', 'name', 'description', 'img_url'])
    reviews = db.get_reviews()
    nearest_recipes['rating'] = reviews[reviews.recipe_id.isin(nearest_recipe_ids)].groupby('recipe_id').rating.mean()[nearest_recipe_ids].fillna(0).values
    nearest_recipes = [{
        'id': x[0],
        'name': x[1],
        'desc': x[2],
        'img_url': x[3],
        'rating': range(int(np.round(x[4]))),
        'rating_null': range(5 - int(np.round(x[4])))
    } for x in nearest_recipes.values]
    return nearest_recipes

def get_similar_tags(recipe_id, recipes):
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
        train_id = recipes['id'].values
    )[0][-15:]
    nearest_recipes = db.get_recipes(recipe_ids=nearest_recipe_ids, columns=['id', 'name', 'description', 'img_url'])
    reviews = db.get_reviews()
    nearest_recipes['rating'] = reviews[reviews.recipe_id.isin(nearest_recipe_ids)].groupby('recipe_id').rating.mean()[nearest_recipe_ids].fillna(0).values
    nearest_recipes = [{
        'id': x[0],
        'name': x[1],
        'desc': x[2],
        'img_url': x[3],
        'rating': range(int(np.round(x[4]))),
        'rating_null': range(5 - int(np.round(x[4])))
    } for x in nearest_recipes.values]
    return nearest_recipes

def get_similar_nutrition(recipe_id, recipes):
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
    nearest_recipes = db.get_recipes(recipe_ids=nearest_recipe_ids, columns=['id', 'name', 'description', 'img_url'])
    reviews = db.get_reviews()
    nearest_recipes['rating'] = reviews[reviews.recipe_id.isin(nearest_recipe_ids)].groupby('recipe_id').rating.mean()[nearest_recipe_ids].fillna(0).values
    nearest_recipes = [{
        'id': x[0],
        'name': x[1],
        'desc': x[2],
        'img_url': x[3],
        'rating': range(int(np.round(x[4]))),
        'rating_null': range(5 - int(np.round(x[4])))
    } for x in nearest_recipes.values]
    return nearest_recipes

def clear_similar_recipes_cache():
    cache.delete('KNNBaseline')
    cache.delete('NRIngr')
    cache.delete('ingr')
    cache.delete('NRTags')
    cache.delete('tags')
    cache.delete('NRNutr')
