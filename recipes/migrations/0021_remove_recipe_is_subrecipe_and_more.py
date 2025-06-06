# Generated by Django 5.0.6 on 2025-02-20 04:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0020_recipesubrecipe_delete_mesurment_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='is_subrecipe',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='related_sub_recipes',
        ),
        migrations.AlterField(
            model_name='recipesubrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='linked_recipes', to='recipes.recipe'),
        ),
        migrations.CreateModel(
            name='SubRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('recipes', models.ManyToManyField(through='recipes.RecipeSubRecipe', to='recipes.recipe')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='recipesubrecipe',
            name='sub_recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='linked_sub_recipes', to='recipes.subrecipe'),
        ),
    ]
