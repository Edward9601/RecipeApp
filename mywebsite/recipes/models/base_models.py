from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


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

class Step(models.Model):
    order = models.PositiveIntegerField()
    description = models.TextField()

    class Meta:
        abstract = True
        ordering = ['order']

    def __str__(self) -> str:
        return f'Step {self.order} {self.description}'