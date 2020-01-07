from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Recipe

def home(request):
    context = {
        'recipes': Recipe.objects.all()
    }
    return render(request, 'blog/home.html', context)

class RecipeListView(ListView):
    model = Recipe
    template_name = 'blog/home.html'
    context_object_name = 'recipes'
    ordering = ['-date']

class RecipeDetailView(DetailView):
    model = Recipe

# Form to create a new recipe
class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    fields = ['name', 'description', 'ingredient_ids', 'tag_ids', 'nutrition', 'calorie_level', 'minutes', 'steps']
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class RecipeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Recipe
    fields = ['name', 'description', 'ingredient_ids', 'tag_ids', 'nutrition', 'calorie_level', 'minutes', 'steps']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        recipe = self.get_object()
        if self.request.user == recipe.user:
            return True
        return False

class RecipeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Recipe
    success_url = '/'
    def test_func(self):
        recipe = self.get_object()
        if self.request.user == recipe.user:
            return True
        return False

def about(request):
    return render(request, 'blog/about.html', {'title':'About'})
