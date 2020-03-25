from blog.models import Home, Ingredient, Recipe, Review, Tag
from django.db import connection
from pandas import DataFrame

def get_home_cache(columns=['recommended', 'favourites', 'make_again', 'top_rated']):
    """
    Retrieve cache info from blog_home table.

    Return cache info as dictionary if cache exists
    Return empty dictionary if cache does not exist
    """
    # Perform Query
    query = f'''
        SELECT {(', ').join(columns)}
        FROM blog_home
        WHERE id = 1;
        '''
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            row = cursor.fetchone()
            cache_dict = dict(zip(columns, row))
        return cache_dict
    except:
        return dict()

def update_home_cache(columns, values):
    """
    Update blog_home table.
    Insert a new row if no cache exists.
    Update existing row if cache exists.

    Keyword arguments:
    columns: str[] -- the list of columns to be updated (same length as values)
    values: int[][] -- the list of values to be updated (same length as columns)

    Return True if update is successful
    Return False if update failed
    """
    # Generate Subquery for UPDATE Query
    subquery_set_list = [f'{columns[i]} = ARRAY{values[i]}::integer[]' for i in range(len(columns))]
    subquery_set = (', ').join(subquery_set_list)
    # Generate Subquery for INSERT Query
    h_columns = ['recommended', 'favourites', 'make_again', 'top_rated']
    invalid_columns = [col for col in columns if col not in h_columns]
    for col in invalid_columns:
        index = columns.index(col)
        del columns[index]
        del values[index]
    default_columns = [col for col in h_columns if col not in columns]
    for col in default_columns:
        values.insert(h_columns.index(col), [])
    subquery_values = (', ').join([f'ARRAY{value}::integer[]' for value in values])
    # Perform Query
    query = f'''
        DO $$
        BEGIN
            IF (EXISTS (SELECT * FROM blog_home WHERE id = 1)) THEN
                UPDATE blog_home
                SET {subquery_set}
                WHERE id = 1;
            ELSE
                INSERT INTO blog_home (recommended, favourites, make_again, top_rated)
                VALUES({subquery_values});
            END IF;
        END$$;
        '''
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
        return True
    except:
        return False

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
            ORDER BY array_position(ARRAY[{ingredient_ids_str}]::integer[], id)
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
            ORDER BY array_position(ARRAY[{recipe_ids_str}]::integer[], id)
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
            ORDER BY array_position(ARRAY[{review_ids_str}]::integer[], id)
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
            ORDER BY array_position(ARRAY[{tag_ids_str}]::integer[], id)
            '''
    data = { column: [] for column in columns }
    rawQuerySet = Tag.objects.raw(query)
    for rawQuery in rawQuerySet:
        for column in columns:
            data[column].append(getattr(rawQuery, column))
    tags_data_frame = DataFrame(data)        
    return tags_data_frame
