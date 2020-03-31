from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path('', views.home, name='blog-home'),
    path('recipe/<int:pk>/', views.recipe_detail_view, name='recipe-detail'),
    path('about/', views.about, name='blog-about')
]
