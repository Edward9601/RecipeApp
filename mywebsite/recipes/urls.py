from django.urls import path
from . import views

'app/model_viewtype'


urlpatterns = [
    path('', views.RecipeListView.as_view(), name='home'),
    path('', views.RecipeListView.as_view(), name='title_search'),
    path('recipe/<int:pk>', views.RecipeDetailView.as_view(), name='detail'),
    path('recipe/create', views.RecipeCreateView.as_view(), name='create'),
    path('recipe/<int:pk>/update/', views.RecipeUpdateView.as_view(), name='update'),
    path('recipe/<int:pk>/delete/', views.RecipeDeleteView.as_view(), name='delete'),

    path('sub-recipes', views.SubRecipeListView.as_view(), name='sub_recipes'),
    path('sub-recipes', views.SubRecipeListView.as_view(), name='sub_recipe_title_search'),
    path('sub-recipes/<int:pk>', views.SubRecipeDetailView.as_view(), name='sub_recipes_detail'),
    path('sub-recipes/create', views.SubRecipeCreateView.as_view(), name='create_sub_recipe'),
    path('sub-recipes/<int:pk>/update', views.SubRecipeUpdateView.as_view(), name='update_sub_recipe'),
    path('sub-recipes/<int:pk>/delete', views.SubRecipeDeleteView.as_view(), name='delete_sub_recipe'),
    
]
