from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.postgres.fields import ArrayField

class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True)
    ingredient_ids = ArrayField(models.PositiveIntegerField())
    tag_ids = ArrayField(models.PositiveIntegerField())
    nutrition = ArrayField(models.FloatField())
    calorie_level = models.PositiveIntegerField()
    minutes = models.PositiveIntegerField()
    steps = ArrayField(models.TextField())
    img_url = models.TextField(default='https://images.pexels.com/photos/574114/pexels-photo-574114.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('recipe-detail', kwargs={'pk': self.pk})

class Ingredient(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Review(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.FloatField()
    review = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id
