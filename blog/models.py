from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.postgres.fields import ArrayField

class Home(models.Model):
    recommended = ArrayField(models.PositiveIntegerField(), null=True)
    favourites = ArrayField(models.PositiveIntegerField(), null=True)
    make_again = ArrayField(models.PositiveIntegerField(), null=True)
    top_rated = ArrayField(models.PositiveIntegerField(), null=True)

class Recipe(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True)
    ingredient_ids = ArrayField(models.PositiveIntegerField())
    tag_ids = ArrayField(models.PositiveIntegerField())
    nutrition = ArrayField(models.FloatField())
    calorie_level = models.PositiveIntegerField()
    minutes = models.PositiveIntegerField()
    steps = ArrayField(models.TextField())
    img_url = models.TextField(default='https://github.com/irkules/randompantry/raw/2.0/staticfiles/img/recipe-image-default.jpeg')
    date = models.DateTimeField(auto_now_add=True)
    user_id = models.PositiveIntegerField()
    # Database Caching
    similar_rating = ArrayField(models.PositiveIntegerField(), null=True)
    similar_ingredients = ArrayField(models.PositiveIntegerField(), null=True)
    similar_tags = ArrayField(models.PositiveIntegerField(), null=True)
    similar_nutrition = ArrayField(models.PositiveIntegerField(), null=True)
    
    def get_absolute_url(self):
        return reverse('recipe-detail', kwargs={ 'pk': self.pk })

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Review(models.Model):
    rating = models.FloatField()
    review = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    recipe_id = models.PositiveIntegerField()
    user_id = models.PositiveIntegerField()

    def __str__(self):
        return self.id
