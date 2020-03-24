from django.core.cache import cache
from django.shortcuts import render
import numpy as np
import pandas as pd
from .models import Recipe, Review
from .forms import UserReviewForm
from . import content

def home(request):
    top_tags = content.get_top_tags()
    context = {
        'title': 'RANDOM PANTRY!',
        'recommendations': content.get_recommended(),
        'favourites': content.get_favourites(),
        'make_again': content.get_make_again(),
        'top_rated': content.get_top_rated(),
        'top_tag_1': top_tags[0],
        'top_tag_2': top_tags[1],
        'top_tag_3': top_tags[2]

    }
    return render(request, 'blog/home.html', context)

# TODO: This needs improvement
# TODO: Add to favourites
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
            # Remove outdated cached data
            content.clear_recommended_cache()
            content.clear_similar_recipes_cache()
    else:
        form = UserReviewForm()
    
    # Recipe-detail content
    recipe = Recipe.objects.get(pk=pk)
    reviews = pd.DataFrame(list(Review.objects.all().values()))
    if len(reviews[reviews.recipe_id == pk]) == 0:
        rating = []
        rating_null = []
    else:
        val = int(np.round(pd.DataFrame(list(Review.objects.all().filter(recipe_id=pk).values())).rating.mean()))
        rating = range(val)
        rating_null = range(5 - val)

    context = {
        'title': 'RANDOM PANTRY! - Recipe',
        'recipe': recipe,
        'author': 'Food.com',
        'rating': rating,
        'rating_null': rating_null,
        'ingredients': content.get_ingr(recipe.ingredient_ids),
        'tags': content.get_tags(recipe.tag_ids),
        'form': form,
        'has_rated': len(reviews[np.logical_and(reviews.user_id == 1, reviews.recipe_id == pk)]) != 0,
        'similar_rating': content.get_similar_rating(pk),
        'similar_ingr': content.get_similar_ingr(pk),
        'similar_tags': content.get_similar_tags(pk),
        'similar_nutr': content.get_similar_nutr(pk)
    }
    return render(request, 'blog/recipe_detail.html', context)

def about(request):
    return render(request, 'blog/about.html', {'title': 'Recipe - About'})
