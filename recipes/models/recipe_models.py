from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from utils.models import AbstractImageModel

from .sub_recipe_models import SubRecipe
from .base_models import BaseRecipe, Ingredient, Step

import os
import uuid

"""
When first migration is ran go to recipes/management/commands/populate_categories.py to see instractions 
on how to prepopulate Category table with initial data.
"""

class Category(models.Model): 
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name



class Recipe(BaseRecipe):
    description = models.TextField(blank=True, null=True)
    sub_recipes = models.ManyToManyField(SubRecipe, through='RecipeSubRecipe',
                                         related_name='main_recipes', blank=True)
    categories = models.ManyToManyField(Category, related_name='recipes', blank=True)
    tags = models.ManyToManyField(Tag, related_name='recipes', blank=True)


class RecipeImage(AbstractImageModel):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='images')

    def save(self, *args, **kwargs):
        if self.picture and hasattr(self, 'recipe') and self.recipe:
            orig = self.picture
            ext = os.path.splitext(orig.name)[1]
            base_name = self.slugify(self.recipe.title)
            unique_id = uuid.uuid4().hex[:8]
            new_name = f'{base_name}_{unique_id}{ext}'
            self.picture.name = new_name

            super().save(*args, **kwargs)
            # Create thumbnail after saving the image
            if self.picture:
                folder = 'recipes_pictures_thumbs_medium'
                self.create_thumbnail(folder, new_name, size=(600, 600), )
    

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
        instance.picture.delete(save=False)