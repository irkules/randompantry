from blog.models import Home, Ingredient, Recipe, Review, Tag
from django.db import connection


# Constants
SEPERATOR = ', '


# DB Column Names
HOME_COLUMNS = [x.name for x in Home._meta.get_fields()]
RECIPE_COLUMNS = [x.name for x in Recipe._meta.get_fields()]
REVIEW_COLUMNS = [x.name for x in Review._meta.get_fields()]


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
        return dict(zip(columns, row))
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
    h_columns = ['recommended', 'recommended_mlp', 'make_again', 'top_rated']
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
        DO 
        $$
        BEGIN
            IF (EXISTS (SELECT * FROM blog_home WHERE id = 1)) THEN
                UPDATE blog_home
                SET {subquery_set}
                WHERE id = 1;
            ELSE
                INSERT INTO blog_home (recommended, recommended_mlp, make_again, top_rated)
                VALUES({subquery_values});
            END IF;
        END
        $$;
        '''
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
        return True
    except:
        return False

def get_top_rated(columns=['id', 'name', 'description', 'img_url', 'rating'], n=20, update_only=False):
    """
    Retrieve Top Rated Recipes from blog_recipe table.
    NOTE: This function updates cache after retrieval.

    Keyword arguments:
    columns: str[] -- the list of columns to be returned
    n: int -- the number of recipes to be returned

    If update_only:
        Return True if updated
        Return False if update failed
    Else:
        Return Array of Dictionary if retrieved successfully
        Return Empty Array if retrieval failed
    """
    query = f'''
        DO 
        $$ 
        DECLARE 
            top_rated_ids INTEGER[];
        BEGIN
            DROP TABLE IF EXISTS top_rated;
            CREATE TEMP TABLE top_rated AS
                SELECT {SEPERATOR.join(columns)}
                FROM (
                    SELECT recipe_id, AVG(rating) as rating
                    FROM blog_review
                    GROUP BY recipe_id
                    ORDER BY COUNT(rating) DESC
                    LIMIT {n}
                ) as review_table
                LEFT JOIN (
                    SELECT *
                    FROM blog_recipe
                ) as recipe_table
                ON review_table.recipe_id = recipe_table.id;
            top_rated_ids := ARRAY(SELECT id FROM top_rated);	
            IF (EXISTS (SELECT id FROM blog_home WHERE id = 1)) THEN
                UPDATE blog_home
                SET top_rated = top_rated_ids
                WHERE id = 1;
            ELSE
                INSERT INTO blog_home (recommended, recommended_mlp, make_again, top_rated)
                VALUES(ARRAY[]::integer[], ARRAY[]::integer[], ARRAY[]::integer[], top_rated_ids);
            END IF;
        END
        $$;
        '''
    if update_only:
        query += '''
            DROP TABLE top_rated;
            '''
    else:
        query += '''
            SELECT * FROM top_rated;
            '''
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            if update_only:
                return True
            else:
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
    except:
        if update_only:
            return False
        else:
            return []

def get_make_again(columns=['id', 'name', 'description', 'img_url', 'rating'], n=20, update_only=False):
    """
    Retrieve Previously Rated Recipes from blog_recipe table.
    NOTE: This function updates cache after retrieval.

    Keyword arguments:
    columns: str[] -- the list of columns to be returned
    n: int -- the number of recipes to be returned

    If update_only:
        Return True if updated
        Return False if update failed
    Else:
        Return Array of Dictionary if retrieved successfully
        Return Empty Array if retrieval failed
    """
    query = f'''
        DO 
        $$ 
        DECLARE 
            make_again_ids INTEGER[];
        BEGIN
            DROP TABLE IF EXISTS make_again;
            CREATE TEMP TABLE make_again AS
                SELECT {SEPERATOR.join(columns)}
                FROM (
                    SELECT recipe_id, rating
                    FROM blog_review
                    WHERE user_id = 1
                    ORDER BY date DESC
                    LIMIT {n}
                ) as review_table
                LEFT JOIN (
                    SELECT *
                    FROM blog_recipe
                ) as recipe_table
                ON review_table.recipe_id = recipe_table.id;
            make_again_ids := ARRAY(SELECT id FROM make_again);	
            IF (EXISTS (SELECT id FROM blog_home WHERE id = 1)) THEN
                UPDATE blog_home
                SET make_again = make_again_ids
                WHERE id = 1;
            ELSE
                INSERT INTO blog_home (recommended, recommended_mlp, make_again, top_rated)
                VALUES(ARRAY[]::integer[], ARRAY[]::integer[], make_again_ids, ARRAY[]::integer[]);
            END IF;
        END
        $$;
        '''
    if update_only:
        query += '''
            DROP TABLE make_again;
            '''
    else:
        query += '''
            SELECT * FROM make_again;
            '''
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            if update_only:
                return True
            else:
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
    except:
        if update_only:
            return False
        else:
            return []

# endregion Home

# region Recipe Details Page

def get_recipe(recipe_id):
    query = f'''
        SELECT
            recipe.id, recipe.name, recipe.date, recipe.description, recipe.img_url, recipe.steps, recipe.nutrition,
            review.rating, rating.has_rated, ARRAY_AGG(DISTINCT ingredients) as ingredients, ARRAY_AGG(DISTINCT tags) as tags,
            recipe.similar_rating, recipe.similar_ingredients, recipe.similar_tags, recipe.similar_nutrition
        FROM (
            SELECT *
            FROM blog_recipe
            WHERE id = {recipe_id}
        ) as recipe
        LEFT JOIN (
            SELECT recipe_id, rating AS has_rated
            FROM blog_review
            WHERE user_id = 1 AND recipe_id = {recipe_id}
        ) as rating
        ON rating.recipe_id = recipe.id
        LEFT JOIN (
            SELECT recipe_id, AVG(rating) AS rating
            FROM blog_review
            WHERE recipe_id = {recipe_id}
            GROUP BY recipe_id
        ) AS review
        ON review.recipe_id = recipe.id
        LEFT JOIN (
            SELECT id, name as ingredients
            FROM blog_ingredient
        ) as ingredient
        ON ingredient.id = ANY(recipe.ingredient_ids)
        LEFT JOIN (
            SELECT id, name as tags
            FROM blog_tag
        ) as tag
        ON tag.id = ANY(recipe.tag_ids)
        GROUP BY
            recipe.id, recipe.name, recipe.date, recipe.description, recipe.img_url, recipe.steps, recipe.nutrition,
            review.rating, rating.has_rated,
            recipe.similar_rating, recipe.similar_ingredients, recipe.similar_tags, recipe.similar_nutrition
        '''
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()
        return dict(zip(columns, row))
    except:
        return dict()

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

def insert_review(rating, recipe_id, user_id):
    query = f'''
        INSERT INTO blog_review (rating, review, date, recipe_id, user_id)
        VALUES({rating}, NULL, NOW(), {recipe_id}, {user_id});
        '''
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
        return True
    except:
        return False

# endregion Recipe Details Page


# region Shared

def get_recipes(recipe_ids=None, columns=RECIPE_COLUMNS):
    # TODO: Refactor this!
    if recipe_ids == []:
        return []
    query = f'''
        SELECT {SEPERATOR.join(columns)}, rating
        FROM (
            SELECT *
            FROM blog_recipe
        ) AS recipe_table
        LEFT JOIN
        (
            SELECT recipe_id, AVG(rating) as rating
            FROM blog_recipe, blog_review 
            WHERE blog_recipe.id = blog_review.recipe_id
            GROUP BY recipe_id
        ) AS review_table
        ON review_table.recipe_id = recipe_table.id
        '''
    if recipe_ids is not None:
        recipe_ids_str = SEPERATOR.join(str(id) for id in recipe_ids)
        query += f'''
            WHERE id IN ({recipe_ids_str})
            ORDER BY array_position(ARRAY[{recipe_ids_str}]::integer[], id)
            '''
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    except:
        return []

def get_reviews(review_ids=None, columns=REVIEW_COLUMNS):
    query = f'''
        SELECT {SEPERATOR.join(columns)}
        FROM blog_review
        '''
    if review_ids is not None:
        ids_str = SEPERATOR.join(str(id) for id in review_ids)
        query += f'''
            WHERE id IN ({ids_str})
            ORDER BY array_position(ARRAY[{ids_str}]::integer[], id)
            '''
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    except:
        return []

# endregion Shared
