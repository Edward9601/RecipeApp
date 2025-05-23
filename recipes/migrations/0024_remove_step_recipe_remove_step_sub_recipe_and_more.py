# Generated by Django 5.0.6 on 2025-02-28 03:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0023_alter_ingredient_recipe_alter_step_recipe'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='step',
            name='recipe',
        ),
        migrations.RemoveField(
            model_name='step',
            name='sub_recipe',
        ),
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=70)),
                ('quantity', models.CharField(blank=True, max_length=20, null=True)),
                ('measurement', models.CharField(blank=True, choices=[('cup', 'Cup'), ('gram', 'Gram'), ('tbs', 'Tablespoon'), ('tsp', 'Teaspoon'), ('Milliliter', 'Milliliter'), ('liter', 'Liter'), ('Pound', 'Pound'), ('bag', 'Bag'), ('piece(s)', 'Piece(s)'), ('slice(s)', 'Slices')], max_length=50, null=True)),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='recipes.recipe')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RecipeStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField()),
                ('description', models.TextField()),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='recipes.recipe')),
            ],
            options={
                'ordering': ['order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SubRecipeIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=70)),
                ('quantity', models.CharField(blank=True, max_length=20, null=True)),
                ('measurement', models.CharField(blank=True, choices=[('cup', 'Cup'), ('gram', 'Gram'), ('tbs', 'Tablespoon'), ('tsp', 'Teaspoon'), ('Milliliter', 'Milliliter'), ('liter', 'Liter'), ('Pound', 'Pound'), ('bag', 'Bag'), ('piece(s)', 'Piece(s)'), ('slice(s)', 'Slices')], max_length=50, null=True)),
                ('sub_recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='recipes.subrecipe')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SubRecipeStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField()),
                ('description', models.TextField()),
                ('sub_recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_steps', to='recipes.subrecipe')),
            ],
            options={
                'ordering': ['order'],
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='Ingredient',
        ),
        migrations.DeleteModel(
            name='Step',
        ),
    ]
