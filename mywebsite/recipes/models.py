from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.signals import pre_delete
from django.contrib.auth.models import User
from django.urls import reverse
from django.dispatch import receiver

import os

MEASUREMENT_CHOICES = [
    ('cup', 'Cup'),
    ('gram', 'Gram'),
    ('tbs', 'Tablespoon'),
    ('tsp', 'Teaspoon'),
    ('Milliliter', 'Milliliter'),
    ('liter', 'Liter'),
    ('Pound', 'Pound'),
    ('bag', 'Bag'),
    ('piece(s)', 'Piece(s)'),
    ('slice(s)', 'Slices')
]


class BaseRecipe(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('detail', kwargs={'pk': self.pk})


class Recipe(BaseRecipe):
    description = models.TextField(blank=True, null=True)
    picture = models.ImageField(upload_to='recipes_pictures/', blank=True, null=True)
    sub_recipes = models.ManyToManyField('SubRecipe', through='RecipeSubRecipe',
                                         related_name='main_recipes', blank=True)


class SubRecipe(BaseRecipe):
    pass


class RecipeSubRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='linked_recipes')
    sub_recipe = models.ForeignKey(SubRecipe, on_delete=models.CASCADE, related_name='linked_sub_recipes')
    specific_notes = models.TextField(blank=True, null=True) # not used yet
    sub_recipe_quantity = models.CharField(max_length=20, null=True, blank=True) # not used yet
    sub_recipe_measurement = models.CharField(max_length=50, choices=MEASUREMENT_CHOICES, null=True, blank=True) # not used yet

    class Meta:
        constraints = [
            UniqueConstraint(fields=['recipe', 'sub_recipe'], name='unique_parent_child_relation')
        ]


class Ingredient(models.Model):
    name = models.CharField(max_length=70)
    quantity = models.CharField(max_length=20, null=True, blank=True)
    measurement = models.CharField(max_length=50, choices=MEASUREMENT_CHOICES, null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        quantity_display = f'{self.quantity}' if self.quantity else ''
        measurement_display = f'{self.measurement}' if self.measurement else ''
        return f'{quantity_display}{measurement_display}{self.name}'.strip()


class RecipeIngredient(Ingredient):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')


class SubRecipeIngredient(Ingredient):
    sub_recipe = models.ForeignKey(SubRecipe, on_delete=models.CASCADE, related_name='sub_ingredients')


class Step(models.Model):
    order = models.PositiveIntegerField()
    description = models.TextField()

    class Meta:
        abstract = True
        ordering = ['order']

    def __str__(self) -> str:
        return f'Step {self.order} {self.description}'


class RecipeStep(Step):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='steps')


class SubRecipeStep(Step):
    sub_recipe = models.ForeignKey(SubRecipe, on_delete=models.CASCADE, related_name='sub_steps')


# Signal handler to delete the image file before the model instance is deleted
@receiver(pre_delete, sender=Recipe)
def delete_image_on_delete_model(sender, instance, **kwargs):
    if instance.picture:
        if os.path.isfile(instance.picture.path):
            os.remove(instance.picture.path)
