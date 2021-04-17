from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('addWatchedMovie', views.AddMovieView.as_view(), name='add'),
    path('addPreference', views.AddPreferenceView.as_view(), name='preference'),
    path('getRecommendations', views.ReccommendationsView.as_view(), name='recommendetion'),
    #path('transform', views.TransformView)
]
