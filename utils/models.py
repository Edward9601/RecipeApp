from django.db import models
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image, ExifTags
from pillow_heif import register_heif_opener
from io import BytesIO
import os
import re

register_heif_opener()

class AbstractImageModel(models.Model): # 
    """
    Abstract model to handle image uploads and thumbnail creation.
    """
    picture = models.ImageField(upload_to='recipes_pictures_originals/', blank=True, null=True)

    class Meta:
        abstract = True


    def create_thumbnail(self, folder, image_name, size=(600, 600)):
        if not self.picture:
            return
        image_name = image_name.split('/')[1]
        self.picture.seek(0)
        img = Image.open(self.picture)
        img = ImageHandler.fix_image_orientation(img)
        img.thumbnail(size)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=90)
        buffer.seek(0)
        thumb_name = f'{folder}/{image_name}'
        default_storage.save(thumb_name, ContentFile(buffer.read()))
        return thumb_name

    def get_thumbnail_url(self, folder):
        if self.picture:
            base, ext = os.path.splitext(os.path.basename(self.picture.name))
            # This assumes you use the same naming as in create_thumbnail
            thumb_name = f"{folder}/{base}.{ext.lstrip('.')}"
            # You may want to implement logic to find the actual file
            # For now, just return the expected path
            return default_storage.url(thumb_name)
        return ''

    def save(self, *args, **kwargs):
        # If a new image is being uploaded, rename it to a user-friendly name
        super().save(*args, **kwargs)

class ImageHandler():
    def __init__(self, image):
        self.image = image

    @staticmethod
    def convert_to_jpeg(image: models.ImageField) -> ContentFile:
        """
        Convert an image from HEIC to JPEG format.
        """
        try:
            img = Image.open(image)
            img = img.convert('RGB')
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=95)
            buffer.seek(0)
            return ContentFile(buffer.read(), name=image.name.replace('.heic', '.jpg'))
        except Exception as e:
            print(f'Error converting image: {e}')
            return None
        
    @staticmethod
    def fix_image_orientation(img):
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = img._getexif()
            if exif is not None:
                orientation_value = exif.get(orientation, None)
                if orientation_value == 3:
                    img = img.rotate(180, expand=True)
                elif orientation_value == 6:
                    img = img.rotate(270, expand=True)
                elif orientation_value == 8:
                    img = img.rotate(90, expand=True)
        except Exception as e:
            print(f'Error fixing orientation: {e}')
        return img
    
    @staticmethod
    def slugify_name(name):
        new_name = str(name)
        new_name = re.sub(r'[^\w\s-]', '', new_name).strip()
        return re.sub(r'[-\s]+', '_', new_name)