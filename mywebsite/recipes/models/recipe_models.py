from django.db import models
from django.db.models.signals import pre_delete

from django.dispatch import receiver
import os
from .sub_recipe_models import SubRecipe
from .base_models import BaseRecipe, Ingredient, Step

"""
When first migration is ran got to recipes/management/commands/populate_categories.py to see instractions 
on how to prepopulate Category table with initial data.
"""

class Category(models.Model): 
    name = models.CharField(max_length=30)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='sub_categories')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'parent'], name='unique_parent_to_sub_categories_relation')
        ]


class Recipe(BaseRecipe):
    description = models.TextField(blank=True, null=True)
    picture = models.ImageField(upload_to='recipes_pictures/', blank=True, null=True)
    sub_recipes = models.ManyToManyField(SubRecipe, through='RecipeSubRecipe',
                                         related_name='main_recipes', blank=True)
    categories = models.ManyToManyField(Category, related_name='recipes')
    
    

class RecipeSubRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='linked_recipes')
    sub_recipe = models.ForeignKey(SubRecipe, on_delete=models.CASCADE, related_name='linked_sub_recipes')

    class Meta:
        constraints = [
           models.UniqueConstraint(fields=['recipe', 'sub_recipe'], name='unique_parent_child_relation')
        ]


class RecipeIngredient(Ingredient):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')


    def __str__(self) -> str:
        quantity_display = self.quantity if self.quantity not in [None, 'None'] else ''
        measurement_display = self.measurement if self.measurement not in [None, 'None'] else ''
        return f'{quantity_display} {measurement_display} {self.name}'.strip()
    

class RecipeStep(Step):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='steps')



# Signal handler to delete the image file before the model instance is deleted
@receiver(pre_delete, sender=Recipe)
def delete_image_on_delete_model(sender, instance, **kwargs):
    if instance.picture:
        if os.path.isfile(instance.picture.path):
            os.remove(instance.picture.path)