from django.db import models

from .base_models import BaseRecipe, Step, Ingredient


class SubRecipe(BaseRecipe):
    pass

class SubRecipeIngredient(Ingredient):
    sub_recipe = models.ForeignKey(SubRecipe, on_delete=models.CASCADE, related_name='sub_ingredients')


class SubRecipeStep(Step):
    sub_recipe = models.ForeignKey(SubRecipe, on_delete=models.CASCADE, related_name='sub_steps')


