from blog.content import HomeContent, RecipeDetailContent
from blog.forms import UserReviewForm
from blog.models import Review
from django.shortcuts import render


def home(request):
    context = HomeContent.get_home_context()
    context['title'] = 'Random Pantry!'
    return render(request, 'blog/home.html', context)

def recipe_detail_view(request, pk):
    context = RecipeDetailContent.get_recipe_detail_context(pk)
    context['title'] = 'Random Pantry! - Recipe'
    context['author'] = 'Food.com'
    if request.method == 'POST':
        form = UserReviewForm(request.POST)
        if form.is_valid():
            RecipeDetailContent.add_review(
                rating=form.cleaned_data['rating'],
                review=form.cleaned_data['review'],
                recipe_id=pk,
                user_id=1
            )
        context['form'] = form
    else:
        context['form'] = UserReviewForm()
    return render(request, 'blog/recipe_detail.html', context)

def about(request):
    return render(request, 'blog/about.html', {'title': 'Recipe - About'})
