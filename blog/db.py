from blog.models import Home, Ingredient, Recipe, Review, Tag
from django.db import connection
from pandas import DataFrame


# Constants
SEPERATOR = ', '


# DB Column Names
HOME_COLUMNS = [x.name for x in Home._meta.get_fields()]
INGREDIENT_COLUMNS = [x.name for x in Ingredient._meta.get_fields()]
RECIPE_COLUMNS = [x.name for x in Recipe._meta.get_fields()]
REVIEW_COLUMNS = [x.name for x in Review._meta.get_fields()]
TAG_COLUMNS = [x.name for x in Tag._meta.get_fields()]


# region Home

def get_home_cache(columns=HOME_COLUMNS):
    """
    Retrieve cache info from blog_home table.

    Return cache info as dictionary if cache exists
    Return empty dictionary if cache does not exist
    """
    query = f'''
        SELECT {SEPERATOR.join(columns)}
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
    subquery_set = SEPERATOR.join(subquery_set_list)
    # Generate Subquery for INSERT Query
    h_columns = ['recommended', 'favourites', 'make_again', 'top_rated']
    invalid_columns = [col for col in columns if col not in h_columns]
    for col in invalid_columns:
        index = columns.index(col)
        del columns[index]
        del values[index]
    default_columns = [col for col in h_columns if col not in columns]
    for col in default_columns:
        values.insert(h_columns.index(col), [-1])
    subquery_values = SEPERATOR.join([f'ARRAY{value}::integer[]' for value in values])
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

# endregion Home

# region Recipe Details Page

def update_recipe_cache(recipe_id, columns, values):
    """
    Update similar recipe ids in blog_recipe table.
    Update similar recipe ids if cache exists.

    Keyword arguments:
    recipe_id: int -- the id of recipe to be updated
    columns: str[] -- the list of columns to be updated (same length as values)
    values: int[][] -- the list of values to be updated (same length as columns)

    Return True if update is successful
    Return False if update failed
    """
    # Generate Subquery
    subquery_set_list = [f'{columns[i]} = ARRAY{values[i]}::integer[]' for i in range(len(columns))]
    subquery_set = SEPERATOR.join(subquery_set_list)
    # Perform Query
    query = f'''
        UPDATE blog_recipe
        SET {subquery_set}
        WHERE id = {recipe_id};
        '''
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
        return True
    except:
        return False

# endregion Recipe Details Page


# region Shared

def get_recipes(recipe_ids=[], columns=RECIPE_COLUMNS):
    query = f'''
        SELECT {SEPERATOR.join(columns)}
        FROM (
            SELECT * FROM blog_recipe
        ) as recipe_table
        LEFT JOIN
        (
            SELECT recipe_id, AVG(rating) as rating
            FROM blog_recipe, blog_review 
            WHERE blog_recipe.id = blog_review.recipe_id
            GROUP BY recipe_id
        ) as review_table
        ON review_table.recipe_id = recipe_table.id
        '''
    if len(recipe_ids) > 0:
        recipe_ids_str = SEPERATOR.join(str(id) for id in recipe_ids)
        query += f'''
            WHERE id IN ({recipe_ids_str})
            ORDER BY array_position(ARRAY[{recipe_ids_str}]::integer[], id)
            '''
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            recipes_dict = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return DataFrame(recipes_dict)
    except:
        return DataFrame()

def get_content(table_name, ids, columns):
    query = f'''
        SELECT {SEPERATOR.join(columns)}
        FROM blog_{table_name}
        '''
    if len(ids) > 0:
        ids_str = SEPERATOR.join(str(id) for id in ids)
        query += f'''
            WHERE id IN ({ids_str})
            ORDER BY array_position(ARRAY[{ids_str}]::integer[], id)
            '''
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            result_dict = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return DataFrame(result_dict)
    except:
        return DataFrame()

def get_reviews(review_ids=[], columns=REVIEW_COLUMNS):
    return get_content(table_name='review', ids=review_ids, columns=columns)

def get_ingredients(ingredient_ids=[], columns=INGREDIENT_COLUMNS):
    return get_content(table_name='ingredient', ids=ingredient_ids, columns=columns)

def get_tags(tag_ids=[], columns=TAG_COLUMNS):
    return get_content(table_name='tag', ids=tag_ids, columns=columns)

# endregion Shared
