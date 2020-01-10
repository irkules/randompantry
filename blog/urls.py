from django.urls import path
from django.contrib import admin
from .views import RecipeCreateView, RecipeUpdateView, RecipeDeleteView
from . import views

urlpatterns = [
    path('', views.home, name='blog-home'),
    path('recipe/<int:pk>/', views.recipe_detail_view, name='recipe-detail'),
    path('recipe/new/', views.recipe_create, name='recipe-create'),
    path('recipe/<int:pk>/update/', RecipeUpdateView.as_view(), name='recipe-update'),
    path('recipe/<int:pk>/delete/', RecipeDeleteView.as_view(), name='recipe-delete'),
    path('about/', views.about, name='blog-about'),
]
