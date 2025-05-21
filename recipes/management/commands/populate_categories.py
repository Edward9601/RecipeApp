from django.core.management.base import BaseCommand
from recipes.models.recipe_models import Category

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
        data = {
            'Breakfast': ['Sweet', 'Savory', 'Quick', 'Healthy'],
            'Lunch': ['Light', 'Hearty', 'Vegan', ''],
            'Dinner': ['Quick', 'Low-carb', 'Fancy'],
            'Snack': ['Sweet', 'Salty', 'Energy'],
            'Dessert': ['Chocolate', 'Fruit-based', 'Cold', 'Warm'],
        }

        for parent_name, childent_names in data.items():
            parent, _ = Category.objects.get_or_create(name=parent_name, parent=None)
            for child_name in childent_names:
                Category.objects.get_or_create(name=child_name, parent=parent)

        self.stdout.write(self.style.SUCCESS('Categories loaded!'))
