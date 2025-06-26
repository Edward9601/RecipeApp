from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

import uuid
import os

from io import BytesIO
from PIL import Image, ExifTags

from .sub_recipe_models import SubRecipe
from .base_models import BaseRecipe, Ingredient, Step

"""
When first migration is ran go to recipes/management/commands/populate_categories.py to see instractions 
on how to prepopulate Category table with initial data.
"""

class Category(models.Model): 
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Recipe(BaseRecipe):
    description = models.TextField(blank=True, null=True)
    picture = models.ImageField(upload_to='recipes_pictures_originals/', blank=True, null=True)
    sub_recipes = models.ManyToManyField(SubRecipe, through='RecipeSubRecipe',
                                         related_name='main_recipes', blank=True)
    categories = models.ManyToManyField(Category, related_name='recipes', blank=True)
    tags = models.ManyToManyField(Tag, related_name='recipes', blank=True)

    def get_thumbnail_url(self):
        if self.picture:
            filename = self.picture.name  # e.g. recipes_pictures_originals/One-Pan_Tuscan_Chicken.jpeg
            thumb_name = filename.replace('recipes_pictures_originals/', 'recipes_pictures_thumbs_medium/')
            return default_storage.url(thumb_name)  # retuning signed URL from storage backend
        return ''
    

    def fix_image_orientation(self, img):
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = img._getexif()
            if exif is not None:
                orientation_value = exif.get(orientation, None)
                if orientation_value == 3: # Upside down (rotate 180°)
                    img = img.rotate(180, expand=True)
                elif orientation_value == 6: # Rotated 90° Clockwise
                    img = img.rotate(270, expand=True)
                elif orientation_value == 8: # Rotated 90° Counterclockwise
                    img = img.rotate(90, expand=True)
        except Exception as e:
            print(f'Error was encountered while trying to fix image orientation: {e}')
            pass
        return img
    
    #TODO: Move image resizing logic to a separate method
    def save(self, *args, **kwargs): 
        # Resize image only if it exists or is new or changed
        if self.picture and not kwargs.get('raw', False):
            try:
                # Just in case reset the cursor to the beginning of the file
                self.picture.seek(0)
                current_image_data = self.picture.read()
                current_image_hash = hash(current_image_data)

                old_hash = None
                if self.pk:
                    # If the recipe already exists, check if the picture has changed
                    old_picture = Recipe.objects.get(pk=self.pk).picture
                    if old_picture:
                        old_picture.seek(0)
                        old_hash = hash(old_picture.read())
                if old_hash is not None and current_image_hash != old_hash:
                    _, ext = os.path.splittext(old_picture.name)
                    safe_title = self.title.replace(' ', '_')
                    unique_id = uuid.uuid4().hex[:8]
                    self.picture.name = f"{safe_title}_{unique_id}{ext}"

                    # Resize and save the thumbnail
                    img = Image.open(BytesIO(current_image_data))
                    img = self.fix_image_orientation(img)
                    img.thumbnail((1200, 1200))
                    if img.mode != 'RGB':
                        img = img.convert('RGB')

                    buffer = BytesIO()
                    img.save(buffer, format='JPEG', quality=100)
                    buffer.seek(0)

                    thumb_name = f"recipes_pictures_thumbs_medium/{safe_title}_{unique_id}{ext}"
                    default_storage.save(thumb_name, ContentFile(buffer.read()))


            except Exception as e:
                print(f'Error was encountered: {e}')

        super().save(*args, **kwargs)
    

class RecipeSubRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='linked_recipes')
    sub_recipe = models.ForeignKey(SubRecipe, on_delete=models.CASCADE, related_name='linked_sub_recipes')

    class Meta:
        constraints = [
           models.UniqueConstraint(fields=['recipe', 'sub_recipe'], name='unique_parent_child_relation')
        ]


class RecipeIngredient(Ingredient):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')


    def __str__(self) -> str:
        quantity_display = self.quantity if self.quantity not in [None, 'None'] else ''
        measurement_display = self.measurement if self.measurement not in [None, 'None'] else ''
        return f'{quantity_display} {measurement_display} {self.name}'.strip()
    

class RecipeStep(Step):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='steps')



# Signal handler to delete the image file before the model instance is deleted
@receiver(pre_delete, sender=Recipe)
def delete_image_on_delete_model(sender, instance, **kwargs):
    if instance.picture:
        instance.picture.delete(save=False)