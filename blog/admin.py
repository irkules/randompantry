from django.contrib import admin
from .models import Recipe, Ingredient, Tag, Review

# Register your models here.

admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Review)
