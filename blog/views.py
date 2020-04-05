from blog.content import HomeContent, RecipeDetailContent
from blog.forms import UserReviewForm
from blog.models import Review
from django.shortcuts import render


def home(request):
    context = HomeContent.get_home_context()
    context['title'] = 'RANDOM PANTRY'
    return render(request, 'blog/home.html', context)

def recipe_detail_view(request, pk):
    context = RecipeDetailContent.get_recipe_detail_context(pk)
    context['title'] = 'RANDOM PANTRY - Recipe'
    if request.method == 'POST':
        form = UserReviewForm(request.POST)
        if form.is_valid():
            RecipeDetailContent.add_review(rating=form.cleaned_data['rating'], recipe_id=pk, user_id=1)
            context['has_rated'] = True
        context['form'] = form
    else:
        context['form'] = UserReviewForm()
    return render(request, 'blog/recipe_detail.html', context)

def about(request):
    context = { 'title': 'RANDOM PANTRY - About' }
    return render(request, 'blog/about.html', context)
