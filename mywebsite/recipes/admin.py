from django.contrib import admin
from .models.recipe_models import Recipe
from .models.sub_recipe_models import SubRecipe

admin.site.register(Recipe)
admin.site.register(SubRecipe)