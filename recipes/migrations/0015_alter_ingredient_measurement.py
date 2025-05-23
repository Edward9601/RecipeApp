# Generated by Django 5.0.6 on 2025-01-25 01:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0014_alter_ingredient_name_alter_ingredient_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='measurement',
            field=models.CharField(blank=True, choices=[('cup', 'Cup'), ('gram', 'Gram'), ('tbs', 'Tablespoon'), ('tsp', 'Teaspoon'), ('Milliliter', 'Milliliter'), ('liter', 'Liter'), ('Pound', 'Pound'), ('bag', 'Bag'), ('piece(s)', 'Piece(s)'), ('slice(s)', 'Slices')], default='cup', max_length=50, null=True),
        ),
    ]
