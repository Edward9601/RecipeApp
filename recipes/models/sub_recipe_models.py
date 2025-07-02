from django.db import models

from .base_models import BaseRecipe, Step, Ingredient

#TODO consoder adding self refference to Recipe class, add indicator 
# (true/fale) for subrecipe, and deleting this separate table

class SubRecipe(BaseRecipe): 
    """
    Model to represent a sub-recipe.
    Sub-recipes can be used to break down complex recipes into smaller, manageable parts.
    They can also be reused in multiple recipes.
    Sub-recipes can have their own ingredients and steps, and can be linked to main recipes.
    """
    pass

class SubRecipeIngredient(Ingredient):
    """
    Model to represent ingredients in a sub-recipe.
    Ingredients can have a name, quantity, and measurement unit.
    The sub_recipe field establishes a many-to-one relationship with the SubRecipe model.
    """
    sub_recipe = models.ForeignKey(SubRecipe, on_delete=models.CASCADE, related_name='sub_ingredients')


class SubRecipeStep(Step):
    """
    Model to represent steps in a sub-recipe.
    Steps can have an order and a description of the action to be performed.
    The order field is used to determine the sequence of steps in the sub-recipe.
    The sub_recipe field establishes a many-to-one relationship with the SubRecipe model.
    """
    sub_recipe = models.ForeignKey(SubRecipe, on_delete=models.CASCADE, related_name='sub_steps')


