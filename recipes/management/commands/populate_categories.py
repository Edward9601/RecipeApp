from django.core.management.base import BaseCommand
from recipes.models.recipe_models import Category, Tag

"""
Management command to populate the Category model with a predefined list of
categories and subcategories.

Usage:
    python manage.py populate_categories

This command is typically used to initialize the database with a fixed hierarchy
of recipe categories and subcategories for filtering and classification purposes.

Each top-level category (e.g., 'Breakfast', 'Lunch') will be created with a set
of subcategories (e.g., 'Sweet', 'Quick'). If a category already exists, it will
not be duplicated.

Note:
- Running it multiple times won't create duplicates.
- You should run this after migrating the database.
"""


class Command(BaseCommand):
    help = 'Load preset categories and subcategories'

    def handle(self, *args, **kwargs):
        categories_list = [
            'Breakfast',
            'Lunch or Dinner',
            'Snack',
            'Dessert',
        ]

        tags_list = [
            'Vegan',
            'Gluten-free',
            'Low-carb',
            'Fancy',
            'Salty',
            'Energy',
            'Chocolate',
            'Fruit-based',
            'Cold',
            'Warm',
            'Quick',
            'Healthy',
            'Light',
            'Sweet',
            'Savory',
        ]
        Category.objects.all().delete()  # Clear existing categories
        Tag.objects.all().delete()
        for category in categories_list:
            Category.objects.get_or_create(name=category)

        for tag in tags_list:
            Tag.objects.get_or_create(name=tag)

        self.stdout.write(self.style.SUCCESS('Categories loaded!'))
