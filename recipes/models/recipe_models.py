from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from utils.models import AbstractImageModel
from django.urls import reverse

from .sub_recipe_models import SubRecipe
from .base_models import BaseRecipe, Ingredient, Step


"""
When first migration is ran go to recipes/management/commands/populate_categories.py to see instractions 
on how to prepopulate Category table with initial data.
"""

class Category(models.Model): 
    """"
    Model to represent recipe categories.
    Categories can be used to group recipes by type, cuisine, or any other classification.
    """
    name = models.CharField(max_length=15, unique=True)

    def __str__(self) -> str:
        return self.name

class Tag(models.Model):
    """
    Model to represent recipe tags.
    Tags can be used to add additional metadata to recipes, such as dietary restrictions, flavor profiles
    """
    name = models.CharField(max_length=15, unique=True)

    def __str__(self) -> str:
        return self.name



class Recipe(BaseRecipe):
    """
    Model to represent a recipe.
    Recipes can have multiple ingredients, steps, sub-recipes.
    They can also be categorized and tagged for better organization.
    """
    description = models.TextField(blank=True, null=True)
    sub_recipes = models.ManyToManyField(SubRecipe, through='RecipeSubRecipe',
                                         related_name='main_recipes', blank=True)
    categories = models.ManyToManyField(Category, related_name='recipes', blank=True)
    tags = models.ManyToManyField(Tag, related_name='recipes', blank=True)

    def get_absolute_url(self):
        return reverse('recipes:detail', kwargs={'pk': self.pk})


class RecipeImage(AbstractImageModel):
    """
    Model to represent images associated with a recipe.
    """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='images')

    thumbnail_folder = 'recipes_pictures_thumbs_medium'

    def get_thumbnail_url(self,):

        """
        Returns the URL of the thumbnail image.
        If a folder is provided, it will use that folder; otherwise, it will use the default thumbnail folder.
        """
        return super().get_thumbnail_url(self.thumbnail_folder)
    

class RecipeSubRecipe(models.Model):
    """
    Intermediate model to represent the relationship between a recipe and its sub-recipes.
    This allows for a many-to-many relationship where a recipe can have multiple sub-recipes
    and a sub-recipe can be part of multiple recipes."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='linked_recipes')
    sub_recipe = models.ForeignKey(SubRecipe, on_delete=models.CASCADE, related_name='linked_sub_recipes')

    class Meta:
        constraints = [
           models.UniqueConstraint(fields=['recipe', 'sub_recipe'], name='unique_parent_child_relation')
        ]


class RecipeIngredient(Ingredient):
    """
    Model to represent ingredients in a recipe.
    Ingredients can have a name, quantity, and measurement unit.
    The recipe field establishes a many-to-one relationship with the Recipe model.
    """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')


class RecipeStep(Step):
    """
    Model to represent steps in a recipe.
    Steps can have an order and a description of the action to be performed.
    The order field is used to determine the sequence of steps in the recipe.
    """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='steps')


# Signal handler to delete the image file before the model instance is deleted
@receiver(pre_delete, sender=Recipe)
def delete_image_on_delete_model(sender, instance, **kwargs):
    if instance.images.exists():
        instance.images.all().delete()