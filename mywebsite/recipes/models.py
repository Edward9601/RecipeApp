from django.db import models
from django.db.models.signals import pre_delete
from django.contrib.auth.models import User
from django.urls import reverse
from django.dispatch import receiver

import os


class Recipe(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    picture = models.ImageField(upload_to='recipes_pictures/', blank=True, null=True)
    

    def get_absolute_url(self):
        return reverse('detail', kwargs={'pk': self.pk})
    
    def __str__(self):
        return self.title
    

class Mesurment(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name
    

class Ingredient(models.Model):
    MEASUREMENT_CHOICES = [
        ('cup', 'Cup'),
        ('gram', 'Gram'),
        ('tbs', 'Tablespoon'),
        ('tsp', 'Teaspoon'),
        ('ml', 'Milliliter'),
        ('liter', 'Liter'),
        ('lbs', 'Pound'),
        ('bag', 'Bag'),
        ('piece(s)', 'Piece(s)')
    ]

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    measurement = models.CharField(max_length=50, choices=MEASUREMENT_CHOICES, null=True, blank=True)

    def __str__(self) -> str:
        quantity_display = f"{self.quantity} " if self.quantity else ""
        measurement_display = f"{self.measurement} " if self.measurement else ""
        return f"{quantity_display}{measurement_display}{self.name}".strip()
    

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