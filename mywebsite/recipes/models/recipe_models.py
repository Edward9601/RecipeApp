from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.signals import pre_delete

from django.dispatch import receiver
import os
from .sub_recipe_models import SubRecipe
from .base_models import BaseRecipe, Ingredient, Step


class Recipe(BaseRecipe):
    description = models.TextField(blank=True, null=True)
    picture = models.ImageField(upload_to='recipes_pictures/', blank=True, null=True)
    sub_recipes = models.ManyToManyField('SubRecipe', through='RecipeSubRecipe',
                                         related_name='main_recipes', blank=True)
    
    

class RecipeSubRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='linked_recipes')
    sub_recipe = models.ForeignKey(SubRecipe, on_delete=models.CASCADE, related_name='linked_sub_recipes')

    class Meta:
        constraints = [
            UniqueConstraint(fields=['recipe', 'sub_recipe'], name='unique_parent_child_relation')
        ]


class RecipeIngredient(Ingredient):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')

class RecipeStep(Step):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='steps')



# Signal handler to delete the image file before the model instance is deleted
@receiver(pre_delete, sender=Recipe)
def delete_image_on_delete_model(sender, instance, **kwargs):
    if instance.picture:
        if os.path.isfile(instance.picture.path):
            os.remove(instance.picture.path)