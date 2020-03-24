from blog.models import Home, Ingredient, Recipe, Review, Tag
from pandas import DataFrame

def get_home(columns=['id', 'recommended', 'favourites', 'make_again', 'top_rated']):
    data = { column: [] for column in columns }
    columns_str = str(list(columns))[1:-1].replace("'", "")
    query = f'''
        SELECT id, {columns_str}
        FROM blog_home
    '''
    rawQuerySet = Home.objects.raw(query)
    for rawQuery in rawQuerySet:
        for column in columns:
            data[column].append(getattr(rawQuery, column))
    home_data_frame = DataFrame(data)
    return home_data_frame

def get_ingredients(ingredient_ids=[], columns=['id', 'name']):
    columns_str = str(list(columns))[1:-1].replace("'", "")
    query = f'''
        SELECT id, {columns_str}
        FROM blog_ingredient
    '''
    if len(ingredient_ids):
        ingredient_ids_str = str(list(ingredient_ids))[1:-1]
        query += f'''
            WHERE id IN ({ingredient_ids_str})
            ORDER BY array_position(array[{ingredient_ids_str}], id)
        '''
    data = { column: [] for column in columns }
    rawQuerySet = Ingredient.objects.raw(query)
    for rawQuery in rawQuerySet:
        for column in columns:
            data[column].append(getattr(rawQuery, column))
    ingredients_data_frame = DataFrame(data)
    return ingredients_data_frame

def get_recipes(
    recipe_ids=[], 
    columns=[
        'id', 'name', 'description', 'ingredient_ids', 'tag_ids', 'nutrition',
        'calorie_level', 'minutes', 'steps', 'img_url', 'date', 'user_id',
        'similar_rating', 'similar_ingredients', 'similar_tags', 'similar_nutrition'
    ]):
    columns_str = str(list(columns))[1:-1].replace("'", "")
    query = f'''
        SELECT id, {columns_str}
        FROM blog_recipe
    '''
    if len(recipe_ids):
        recipe_ids_str = str(list(recipe_ids))[1:-1]
        query += f'''
            WHERE id IN ({recipe_ids_str})
            ORDER BY array_position(array[{recipe_ids_str}], id)
        '''
    data = { column: [] for column in columns }
    rawQuerySet = Recipe.objects.raw(query)
    for rawQuery in rawQuerySet:
        for column in columns:
            data[column].append(getattr(rawQuery, column))
    recipes_data_frame = DataFrame(data)       
    return recipes_data_frame

def get_reviews(review_ids=[], columns=['id', 'rating', 'review', 'date', 'recipe_id', 'user_id']):
    columns_str = str(list(columns))[1:-1].replace("'", "")
    query = f'''
        SELECT id, {columns_str}
        FROM blog_review
    '''
    if len(review_ids):
        review_ids_str = str(list(review_ids))[1:-1]
        query += f'''
            WHERE id IN ({review_ids_str})
            ORDER BY array_position(array[{review_ids_str}], id)
        '''
    data = { column: [] for column in columns }
    rawQuerySet = Review.objects.raw(query)
    for rawQuery in rawQuerySet:
        for column in columns:
            data[column].append(getattr(rawQuery, column))
    reviews_data_frame = DataFrame(data)
    return reviews_data_frame

def get_tags(tag_ids=[], columns=['id', 'name']):
    columns_str = str(list(columns))[1:-1].replace("'", "")
    query = f'''
        SELECT id, {columns_str}
        FROM blog_tag
    '''
    if len(tag_ids):
        tag_ids_str = str(list(tag_ids))[1:-1]
        query += f'''
            WHERE id IN ({tag_ids_str})
            ORDER BY array_position(array[{tag_ids_str}], id)
        '''
    data = { column: [] for column in columns }
    rawQuerySet = Tag.objects.raw(query)
    for rawQuery in rawQuerySet:
        for column in columns:
            data[column].append(getattr(rawQuery, column))
    tags_data_frame = DataFrame(data)        
    return tags_data_frame
