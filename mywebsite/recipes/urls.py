from django.urls import path
from .views import recipe_views, sub_recipe_views

'app/model_viewtype'


urlpatterns = [
    path('', recipe_views.RecipeListView.as_view(), name='home'),
    path('', recipe_views.RecipeListView.as_view(), name='recipe_search'),
    path('recipe/<int:pk>', recipe_views.RecipeDetailView.as_view(), name='detail'),
    path('recipe/create', recipe_views.RecipeCreateView.as_view(), name='create'),
    path('recipe/<int:pk>/update/', recipe_views.RecipeUpdateView.as_view(), name='update'),
    path('recipe/<int:pk>/delete/', recipe_views.RecipeDeleteView.as_view(), name='delete'),

    path('sub-recipes', sub_recipe_views.SubRecipeListView.as_view(), name='sub_recipes'),
    path('sub-recipes', sub_recipe_views.SubRecipeListView.as_view(), name='sub_recipe_search'),
    path('sub-recipes/<int:pk>', sub_recipe_views.SubRecipeDetailView.as_view(), name='sub_recipes_detail'),
    path('sub-recipes/create', sub_recipe_views.SubRecipeCreateView.as_view(), name='create_sub_recipe'),
    path('sub-recipes/<int:pk>/update', sub_recipe_views.SubRecipeUpdateView.as_view(), name='update_sub_recipe'),
    path('sub-recipes/<int:pk>/delete', sub_recipe_views.SubRecipeDeleteView.as_view(), name='delete_sub_recipe'),
    
]
