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

class Recipe(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    picture = models.ImageField(upload_to='recipes_pictures/', blank=True, null=True)
    is_subrecipe = models.BooleanField(default=False)
    related_sub_recipes = models.ManyToManyField('self', through='RecipeSubRecipe',
                                        through_fields=('recipe', 'sub_recipe'),
                                        symmetrical=False, related_name='sub_recipes')
    

    def get_absolute_url(self):
        return reverse('detail', kwargs={'pk': self.pk})
    
    def __str__(self):
        return self.title
    

class RecipeSubRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='parent_recipe')
    sub_recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='used_sub_recipes')
    specific_notes = models.TextField(blank=True, null=True)
    sub_recipe_quantity = models.CharField(max_length=20, null=True, blank=True)
    sub_recipe_measurement = models.CharField(max_length=50, choices=MEASUREMENT_CHOICES, null=True, blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['recipe', 'sub_recipe'], name='unique_parent_child_relation')
        ]



class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=70)
    quantity = models.CharField(max_length=20, null=True, blank=True)
    measurement = models.CharField(max_length=50, choices=MEASUREMENT_CHOICES, null=True, blank=True)

    def __str__(self) -> str:
        quantity_display = f'{self.quantity}' if self.quantity else ''
        measurement_display = f'{self.measurement}' if self.measurement else ''
        return f'{quantity_display}{measurement_display}{self.name}'.strip()
    

class Step(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='steps')
    order = models.PositiveIntegerField()
    description = models.TextField()


    def __str__(self) -> str:
        return f'Step {self.order} {self.description}'

# Signal handler to delete the image file before the model instance is deleted
@receiver(pre_delete, sender=Recipe)
def delete_image_on_delete_model(sender, instance, **kwargs):
        if instance.picture:
            if os.path.isfile(instance.picture.path):
                os.remove(instance.picture.path)