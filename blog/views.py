from django.shortcuts import render
import numpy as np
import pandas as pd
from blog.models import Recipe, Review
from blog.forms import UserReviewForm
from blog.content import HomeContent, RecipeDetailContent

def home(request):
    home_context = HomeContent.get_home_context()
    context = {
        'title': 'Random Pantry!',
        'recommendations': home_context[0],
        'favourites': home_context[1],
        'make_again': home_context[2],
        'top_rated': home_context[3]
    }
    return render(request, 'blog/home.html', context)

def recipe_detail_view(request, pk):
    # Review Form
    if request.method == 'POST':
        form = UserReviewForm(request.POST)
        if form.is_valid():
            Review.objects.create(
                rating=form.cleaned_data['rating'],
                review=form.cleaned_data['review'],
                recipe_id=pk,
                user_id=1
            )
            HomeContent.purge_recommended_cache()
            RecipeDetailContent.clear_similar_recipes_cache()
    else:
        form = UserReviewForm()

    recipe_detail_context = RecipeDetailContent.get_recipe_detail_context(pk)
    context = {
        'title': 'Random Pantry! - Recipe',
        'recipe': recipe_detail_context[0],
        'author': 'Food.com',
        'rating': recipe_detail_context[1],
        'rating_null': recipe_detail_context[2],
        'ingredients': recipe_detail_context[3],
        'tags': recipe_detail_context[4],
        'form': form,
        'has_rated': recipe_detail_context[5],
        'similar_rating': recipe_detail_context[6],
        'similar_ingr': recipe_detail_context[7],
        'similar_tags': recipe_detail_context[8],
        'similar_nutr': recipe_detail_context[9]
    }
    return render(request, 'blog/recipe_detail.html', context)

def about(request):
    return render(request, 'blog/about.html', {'title': 'Recipe - About'})
