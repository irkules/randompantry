from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView
import numpy as np
import pandas as pd
from .models import Recipe, Review
from .forms import UserReviewForm
from . import content

def home(request):
    top_tags = content.get_top_tags()
    context = {
        'title': 'RANDOM PANTRY!',
        'my_recipes': [],
        'recommendations': content.get_recommended(request.user.id),
        'favourites': content.get_favourites(request.user.id),
        'make_again': content.get_make_again(request.user.id),
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
                user_id=request.user.id
            )
            messages.success(request, f'Thank you for rating!')
            # Remove outdated cached data
            content.clear_recommended_cache()
            content.clear_similar_recipes_cache()
    else:
        form = UserReviewForm()
    
    # Recipe-detail content
    recipe = Recipe.objects.get(pk=pk)
    rating = int(np.round(pd.DataFrame(list(Review.objects.all().filter(recipe_id=pk).values())).rating.mean()))
    context = {
        'title': 'RANDOM PANTRY! - Recipe',
        'recipe': recipe,
        'rating': range(rating),
        'rating_null': range(5 - rating),
        'ingredients': content.get_ingr(recipe.ingredient_ids),
        'tags': content.get_tags(recipe.tag_ids),
        'form': form,
        'has_rated': len(list(Review.objects.all().filter(user_id=request.user.id, recipe_id=pk).values())) != 0,
        'similar_rating': content.get_similar_rating(pk),
        'similar_ingr': content.get_similar_ingr(pk),
        'similar_tags': content.get_similar_tags(pk),
        'similar_nutr': content.get_similar_nutr(pk)
    }
    return render(request, 'blog/recipe_detail.html', context)

# Form to create a new recipe
class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    fields = ['name', 'description', 'ingredient_ids', 'tag_ids', 'nutrition', 'calorie_level', 'minutes', 'steps']

    def form_valid(self, form):
        form.instance.user = self.request.user
        content.clear_similar_recipes_cache()
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['title'] = 'RANDOM PANTRY! - Create Recipe'
        return data

class RecipeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Recipe
    fields = ['name', 'description', 'ingredient_ids', 'tag_ids', 'nutrition', 'calorie_level', 'minutes', 'steps']

    def form_valid(self, form):
        form.instance.user = self.request.user
        content.clear_similar_recipes_cache()
        return super().form_valid(form)

    def test_func(self):
        recipe = self.get_object()
        if self.request.user == recipe.user:
            return True
        return False
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['title'] = 'RANDOM PANTRY! - Update Recipe'
        return data

class RecipeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Recipe
    success_url = '/'
    def test_func(self):
        recipe = self.get_object()
        if self.request.user == recipe.user:
            return True
        return False

    def get_context_data(self, **kwargs):
        content.clear_similar_recipes_cache()
        data = super().get_context_data(**kwargs)
        data['title'] = 'RANDOM PANTRY! - Delete Recipe'
        return data

def about(request):
    return render(request, 'blog/about.html', {'title': 'Recipe - About'})
