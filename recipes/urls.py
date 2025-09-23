from django.urls import path
from .views import recipe_views, sub_recipe_views

app_name = 'recipes'


urlpatterns = [
    path('', recipe_views.RecipeListView.as_view(), name='home'),
    path('', recipe_views.RecipeListView.as_view(), name='recipe_search'),
    path('recipe/<int:pk>', recipe_views.RecipeDetailView.as_view(), name='detail'),
    path('recipe/create', recipe_views.RecipeCreateView.as_view(), name='create'),
    path('recipe/<int:pk>/update/', recipe_views.RecipeUpdateView.as_view(), name='update'),
    path('recipe/<int:pk>/delete/', recipe_views.RecipeDeleteView.as_view(), name='delete'),
    path('get-categories-tags/', recipe_views.get_categories_and_tags, name='get_categories_and_tags'),

    path('recipe/ingredients', recipe_views.IngredientsPartialView.as_view(), name='fetch_ingredients_form'),
    path('recipe/ingredients/<int:pk>', recipe_views.IngredientsPartialView.as_view(), name='fetch_recipe_ingredients'),
    path('recipe/ingredients/<int:pk>/update', recipe_views.IngredientsPartialView.as_view(), name='update_recipe_ingredients'),

    path('recipe/steps', recipe_views.StepsPartialView.as_view(), name='fetch_steps_form'),
    path('recipe/steps/<int:pk>', recipe_views.StepsPartialView.as_view(), name='fetch_recipe_steps'),
    path('recipe/steps/<int:pk>/update', recipe_views.StepsPartialView.as_view(), name='update_recipe_steps'),

    path('sub-recipes', sub_recipe_views.SubRecipeListView.as_view(), name='sub_recipes'),
    path('sub-recipes', sub_recipe_views.SubRecipeListView.as_view(), name='sub_recipe_search'),
    path('sub-recipes/<int:pk>', sub_recipe_views.SubRecipeDetailView.as_view(), name='sub_recipes_detail'),
    path('sub-recipes/create', sub_recipe_views.SubRecipeCreateView.as_view(), name='create_sub_recipe'),
    path('sub-recipes/<int:pk>/update', sub_recipe_views.SubRecipeUpdateView.as_view(), name='update_sub_recipe'),
    path('sub-recipes/<int:pk>/delete', sub_recipe_views.SubRecipeDeleteView.as_view(), name='delete_sub_recipe'),
    
]
