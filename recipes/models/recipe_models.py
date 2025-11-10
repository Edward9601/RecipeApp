from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.forms import ValidationError
from utils.models import AbstractImageModel, ImageHandler
from django.urls import reverse

from .base_models import BaseRecipe, Ingredient, Step

import os


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
    parent_recipe = models.ManyToManyField('self', 
                                         through='RecipeSubRecipe',
                                         through_fields=('sub_recipe', 'parent_recipe'),
                                         related_name='sub_recipe',
                                         blank=True,
                                         symmetrical=False)
    is_sub_recipe = models.BooleanField(default=False)
    categories = models.ManyToManyField(Category, related_name='recipes', blank=True)
    tags = models.ManyToManyField(Tag, related_name='recipes', blank=True)

    def get_absolute_url(self):
        if self.is_sub_recipe:
            return reverse('recipes:sub_recipes_detail', kwargs={'pk': self.pk})
        return reverse('recipes:detail', kwargs={'pk': self.pk})


class RecipeImage(AbstractImageModel):
    """
    Model to represent images associated with a recipe.
    """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='images')

    thumbnail_folder = 'recipes_pictures_thumbs_medium'


    def save(self, *args, **kwargs):
        # Only rename if both recipe and picture are set
        if self.picture and self.recipe:
            image_handler = ImageHandler(self.picture)
            orig = self.picture
            ext = os.path.splitext(orig.name)[1]
            base_name = image_handler.slugify_name(self.recipe.title)
            new_name = f'{base_name}{ext}'
            self.picture.name = new_name
        super().save(*args, **kwargs)

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
    parent_recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='parent_recipe_relation', blank=True, default=None)
    sub_recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='sub_recipe_relation', blank=True)

    class Meta:
        constraints = [
           # Ensure unique parent-sub-recipe pairs
           models.UniqueConstraint(fields=['parent_recipe', 'sub_recipe'], name='%(app_label)s_%(class)s_unique_parent_child_relation'),
           # Prevent a recipe from being its own sub-recipe
           models.CheckConstraint(check=~models.Q(parent_recipe=models.F('sub_recipe')), name='%(app_label)s_%(class)s_no_self_reference'),
        ]

    def clean(self):
        # Prevent circular reference (A→B and B→A)
        if RecipeSubRecipe.objects.filter(parent_recipe=self.sub_recipe,
                                          sub_recipe=self.parent_recipe).exists():
            raise ValidationError("Circular sub-recipe relationships are not allowed.")

        # Optional: prevent self-reference
        if self.parent_recipe == self.sub_recipe:
            raise ValidationError("A recipe cannot be a sub-recipe of itself.")

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