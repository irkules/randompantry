from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
import numpy as np
import pandas as pd
from .models import Recipe, Review, Ingredient, Tag
from .forms import UserReviewForm, RecipeCreateForm
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
    reviews = pd.DataFrame(list(Review.objects.all().values()))
    if len(reviews[reviews.recipe_id == pk]) == 0:
        rating = []
        rating_null = []
    else:
        val = int(np.round(pd.DataFrame(list(Review.objects.all().filter(recipe_id=pk).values())).rating.mean()))
        rating = range(val)
        rating_null = range(5 - val)
    
    # Get recipe author
    users = pd.DataFrame(list(User.objects.all().values()))
    if (users.id != recipe.user_id).all():
        author = 'Food.com'
    else:
        author = users.loc[users.id != recipe.user_id, 'username'].values()

    context = {
        'title': 'RANDOM PANTRY! - Recipe',
        'recipe': recipe,
        'author': author,
        'rating': rating,
        'rating_null': rating_null,
        'ingredients': content.get_ingr(recipe.ingredient_ids),
        'tags': content.get_tags(recipe.tag_ids),
        'form': form,
        'has_rated': len(reviews[np.logical_and(reviews.user_id == request.user.id, reviews.recipe_id == pk)]) != 0,
        'similar_rating': content.get_similar_rating(pk),
        'similar_ingr': content.get_similar_ingr(pk),
        'similar_tags': content.get_similar_tags(pk),
        'similar_nutr': content.get_similar_nutr(pk)
    }
    return render(request, 'blog/recipe_detail.html', context)

def strip_punc(sentence):
    punc_list = [".",";",":","!","?","/","\\","#","@","$","&",")","(","\""]
    for punc in punc_list:
        sentence = sentence.replace(punc, '')
    return sentence

def recipe_create(request):
    if request.method == 'POST':
        form = RecipeCreateForm(request.POST)
        if form.is_valid():
            # Convert ingredient names into ids
            ingrs = pd.DataFrame(list(Ingredient.objects.all().values()))
            # Strip punctuations
            new_ingrs = [x.strip() for x in strip_punc(form.cleaned_data['ingrs']).split(',')]
            # Strip empty ingredients
            new_ingrs = [i.lower() for i in new_ingrs if i]
            intersect = ingrs.loc[ingrs.name.isin(new_ingrs), 'name'].values
            minus = np.setdiff1d(new_ingrs, intersect)
            for ingr_name in minus:
                Ingredient.objects.create(name = ingr_name)
            ingrs = pd.DataFrame(list(Ingredient.objects.all().values()))
            ingr_ids = ingrs.loc[ingrs.name.isin(new_ingrs), 'id'].tolist()

            # Convert tag names into ids
            tags = pd.DataFrame(list(Tag.objects.all().values()))
            # Strip punctuations
            new_tags = [x.strip() for x in strip_punc(form.cleaned_data['tags']).split(',')]
            # Strip empty tags
            new_tags = [i.lower() for i in new_tags if i]
            intersect = tags.loc[tags.name.isin(new_tags), 'name'].values
            minus = np.setdiff1d(new_tags, intersect)
            for ingr_name in minus:
                Tag.objects.create(name = ingr_name)
            tags = pd.DataFrame(list(Tag.objects.all().values()))
            tag_ids = tags.loc[tags.name.isin(new_tags), 'id'].tolist()
            
            # Convert steps into array
            steps = form.cleaned_data['steps'].split(',')
            # Strip empty steps
            steps = [i.lower() for i in steps if i]
            print("processing done")
            Recipe.objects.create(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['desc'],
                ingredient_ids=ingr_ids,
                tag_ids=tag_ids,
                nutrition=[
                    form.cleaned_data['calorie'],
                    form.cleaned_data['fat'],
                    form.cleaned_data['sugar'],
                    form.cleaned_data['sodium'],
                    form.cleaned_data['protein'],
                    form.cleaned_data['sat_fat'],
                    form.cleaned_data['carbo']
                ],
                calorie_level=form.cleaned_data['calorie_level'],
                minutes=form.cleaned_data['minutes'],
                steps=steps,
                img_url=form.cleaned_data['img_url'],
                user_id=request.user.id
            )
            messages.success(request, f'Thank you for creating a recipe!')
            # Remove outdated cached data
            content.clear_recommended_cache()
            content.clear_similar_recipes_cache()
    else:
        form = RecipeCreateForm()
    context = {
        'title': 'RANDOM PANTRY! - Create Recipe',
        'form': form
    }
    return render(request, 'blog/recipe_form.html', context)

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
