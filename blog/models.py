from django.db.models import CharField, DateTimeField, FloatField, Model, PositiveIntegerField, TextField
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.postgres.fields import ArrayField

class Home(Model):
    recommended = ArrayField(PositiveIntegerField(), null=True)
    recommended_mlp = ArrayField(PositiveIntegerField(), null=True)
    make_again = ArrayField(PositiveIntegerField(), null=True)
    top_rated = ArrayField(PositiveIntegerField(), null=True)

class Recipe(Model):
    name = CharField(max_length=100)
    description = TextField(null=True)
    ingredient_ids = ArrayField(PositiveIntegerField())
    tag_ids = ArrayField(PositiveIntegerField())
    nutrition = ArrayField(FloatField())
    calorie_level = PositiveIntegerField()
    minutes = PositiveIntegerField()
    steps = ArrayField(TextField())
    img_url = TextField(default='https://github.com/irkules/randompantry/raw/2.0/staticfiles/img/recipe-image-default.jpeg')
    date = DateTimeField(auto_now_add=True)
    user_id = PositiveIntegerField()
    # Database Caching
    similar_rating = ArrayField(PositiveIntegerField(), null=True)
    similar_ingredients = ArrayField(PositiveIntegerField(), null=True)
    similar_tags = ArrayField(PositiveIntegerField(), null=True)
    similar_nutrition = ArrayField(PositiveIntegerField(), null=True)
    
    def get_absolute_url(self):
        return reverse('recipe-detail', kwargs={ 'pk': self.pk })

    def __str__(self):
        return self.name

class Ingredient(Model):
    name = CharField(max_length=100)

    def __str__(self):
        return self.name

class Tag(Model):
    name = CharField(max_length=100)

    def __str__(self):
        return self.name

class Review(Model):
    rating = FloatField()
    review = TextField(null=True)
    date = DateTimeField(auto_now_add=True)
    recipe_id = PositiveIntegerField()
    user_id = PositiveIntegerField()

    def __str__(self):
        return self.id
