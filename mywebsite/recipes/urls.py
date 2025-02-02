from django.urls import path
from . import views

'app/model_viewtype'


urlpatterns = [
    path('', views.RecipeListView.as_view(), name='home'),
    path('partial_search/', views.RecipeListView.as_view(), name='title_search'),
    path('recipe/<int:pk>/', views.RecipeDetailView.as_view(), name='detail'),
    path('recipe/create/', views.RecipeCreateView.as_view(), name='create'),
    path('recipe/<int:pk>/update', views.RecipeUpdateView.as_view(), name='update'),
    path('recipe/<int:pk>/delete', views.RecipeDeleteView.as_view(), name='delete'),
]
