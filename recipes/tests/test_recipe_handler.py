from .base import BaseTestCase
from recipes.models.recipe_models import Recipe, Category, Tag, RecipeImage, RecipeIngredient, RecipeStep, SubRecipe
from recipes.handlers import recipes_handler
from recipes.forms.recipe_forms import RecipeImageForm, RecipeCreateForm
from PIL import Image
import tempfile

from django.test import RequestFactory
from django.db.models.query import QuerySet
from django.core.files.uploadedfile import SimpleUploadedFile

class RecipeHandlerTestCase(BaseTestCase):
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.recipe = Recipe.objects.create(
            title='Test Recipe',
            description='Test Description',
            author=cls.user,
        )
        cls.category = Category.objects.create(name='Test Category')
        cls.tag = Tag.objects.create(name='Test Tag')
        cls.sub_recipe = SubRecipe.objects.create(
            title='Test Sub Recipe',
            author=cls.user,
        )
        obj = cls()
        cls.image = RecipeImage.objects.create(
            recipe=cls.recipe,
            picture=obj.generate_test_image_file(),
        )
        cls.recipe.categories.add(cls.category)
        cls.recipe.tags.add(cls.tag)
        


    def generate_test_image_file(self):
        # Create a temporary image file
        image = Image.new('RGB', (100, 100), color='red')
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(temp_file, format='JPEG')
        temp_file.seek(0)
        return SimpleUploadedFile(
            name='test.jpg',
            content=temp_file.read(),
            content_type='image/jpeg'
        )
    
    def generate_data_for_post_request(self, ingredients_num: int, steps_num: int):
        """
        Generates data for a POST request to create a recipe.
        """
        data = {
            'title': 'Good Recipe',
            'description': 'Description',
            'categories': [f'{self.category.id}'],  # id of the category
            'tags': [f'{self.tag.id}'],  # id of the tag
            'sub_recipes': [f'{self.sub_recipe.id}'],  # id of the sub recipe
            'ingredients-TOTAL_FORMS': str(ingredients_num),
            'ingredients-INITIAL_FORMS': '0',
            'ingredients-MIN_NUM_FORMS': '0',
            'ingredients-MAX_NUM_FORMS': '1000',
            'steps-TOTAL_FORMS': str(steps_num),
            'steps-INITIAL_FORMS': '0',
            'steps-MIN_NUM_FORMS': '0',
            'steps-MAX_NUM_FORMS': '1000',
            'picture': self.image.picture,  # Simulating an image upload
        }
        for i in range(ingredients_num):
            data[f'ingredients-{i}-name'] = f'Ingredient {i+1}'
            data[f'ingredients-{i}-quantity'] = str(i + 1)
            data[f'ingredients-{i}-measurement'] = 'cup'
        for i in range(steps_num):
            data[f'steps-{i}-order'] = str(i + 1)
            data[f'steps-{i}-description'] = f'Step {i+1}'
        return data

    def test_fetch_recipe_context_data_for_post_request(self):
        # Arrange
        data = self.generate_data_for_post_request(ingredients_num=1, steps_num=1)
        request = RequestFactory().post('test/', data=data, formats='multipart')
        # Act
        context = recipes_handler.fetch_recipe_context_data_for_post_request(self.recipe, request, RecipeImageForm, self.image)
        # Assert
        self.assertIsNotNone(context.get('ingredient_formset'))
        self.assertIsNotNone(context.get('step_formset'))
        self.assertIsNotNone(context.get('image_form'))
        self.assertIsInstance(context.get('image_form'), RecipeImageForm)
        self.assertEqual(context.get('image_form').instance, self.image)
        self.assertEqual(context.get('ingredient_formset').instance, self.recipe)
        self.assertEqual(context.get('step_formset').instance, self.recipe)
        self.assertEqual(context.get('ingredient_formset').prefix, 'ingredients')
        self.assertEqual(context.get('step_formset').prefix, 'steps')
        self.assertEqual(context.get('ingredient_formset').queryset.model, RecipeIngredient)
        self.assertEqual(context.get('step_formset').queryset.model, RecipeStep)
        self.assertTrue(context.get('ingredient_formset').is_valid())
        self.assertTrue(context.get('step_formset').is_valid())
        self.assertTrue(context.get('image_form').is_valid())
        self.assertTrue(context.get('ingredient_formset').has_changed())
        self.assertTrue(context.get('step_formset').has_changed())
        self.assertTrue(context.get('image_form').has_changed())


    def test_fetch_recipe_context_data_for_get_request_for_new_recipe(self):
        # Arrange
        recipe = Recipe()

        # Act
        context = recipes_handler.fetch_recipe_context_data_for_get_request(recipe, RecipeImageForm, None)
        categories = context.get('categories')
        tags = context.get('tags')
        ingredient_formset = context.get('ingredient_formset')
        step_formset = context.get('step_formset')
        image_form = context.get('image_form')
        form = context.get('form')

        # Assert
        self.assertIsNotNone(ingredient_formset)
        self.assertIsNotNone(step_formset)
        self.assertIsNotNone(image_form)
        self.assertIsNotNone(categories)
        self.assertIsNotNone(tags)

        self.assertIsInstance(image_form, RecipeImageForm)
        self.assertIsInstance(form, RecipeCreateForm)
        self.assertIsInstance(categories, QuerySet)
        self.assertIsInstance(tags, QuerySet)


        self.assertEqual(form.instance, recipe)
        self.assertEqual(ingredient_formset.prefix, 'ingredients')
        self.assertEqual(step_formset.prefix, 'steps')
        self.assertEqual(ingredient_formset.queryset.model, RecipeIngredient)
        self.assertEqual(step_formset.queryset.model, RecipeStep)


    def test_fetch_recipe_context_data_for_get_request_for_existing_recipe(self):
        # Arrange
        recipe = self.recipe
        image_instance = self.image

        # Act
        context = recipes_handler.fetch_recipe_context_data_for_get_request(recipe, RecipeImageForm, image_instance)
        # Assert
        self.assertIsNotNone(context.get('ingredient_formset'))
        self.assertIsNotNone(context.get('step_formset'))
        self.assertIsNotNone(context.get('image_form'))
        self.assertIsInstance(context.get('image_form'), RecipeImageForm)
        self.assertEqual(context.get('image_form').instance, image_instance)
        self.assertEqual(context.get('ingredient_formset').instance, recipe)
        self.assertEqual(context.get('step_formset').instance, recipe)  
        self.assertEqual(context.get('form').instance, recipe)
        self.assertEqual(context.get('ingredient_formset').prefix, 'ingredients')
        self.assertEqual(context.get('step_formset').prefix, 'steps')
        self.assertEqual(context.get('ingredient_formset').queryset.model, RecipeIngredient)
        self.assertEqual(context.get('step_formset').queryset.model, RecipeStep)
        self.assertEqual(context.get('categories').count(), Category.objects.count())
        self.assertEqual(context.get('tags').count(), Tag.objects.count())
        self.assertEqual(context.get('categories').first(), self.category)
        self.assertEqual(context.get('tags').first(), self.tag)

    def test_save_valid_forms(self):
        # Arrange
        recipe = self.recipe
        data = self.generate_data_for_post_request(ingredients_num=2, steps_num=2)
        request = RequestFactory().post('test/', data=data, formats='multipart')
        context = recipes_handler.fetch_recipe_context_data_for_post_request(recipe, request, RecipeImageForm)
       
        
        # Act
        ingredient_formset = context['ingredient_formset']
        step_formset = context['step_formset']
        ingredient_formset.is_valid()
        step_formset.is_valid()
        forms = [
            ingredient_formset,
            step_formset
        ]
        recipes_handler.save_valid_forms(recipe, forms)

        # Assert
        self.assertTrue(recipe.ingredients.filter(name='Ingredient 1').exists())
        self.assertTrue(recipe.steps.filter(description='Step 1').exists())


    def test_save_image_from(self):
        # Arrange
        recipe = self.recipe
        data = self.generate_data_for_post_request(0, 0)
        request = RequestFactory().post('test/', data=data, formats='multipart')
        context = recipes_handler.fetch_recipe_context_data_for_post_request(recipe, request, RecipeImageForm, self.image)
       
        
        # Act
        image_form = context.get('image_form')

        image_form.is_valid()

        recipes_handler.save_image_form(recipe, image_form)
        # Assert
        self.assertFalse(recipe.ingredients.filter(name='Ingredient 1').exists())
        self.assertFalse(recipe.steps.filter(description='Step 1').exists())
        self.assertTrue(recipe.images.filter(id=self.image.id).exists())


    def test_validate_forms_return_true(self):
        # Arrange
        recipe = self.recipe
        data = self.generate_data_for_post_request(1, 1)
        request = RequestFactory().post('test/', data=data, formats='multipart')
        context = recipes_handler.fetch_recipe_context_data_for_post_request(recipe, request, RecipeImageForm, self.image)

        ingredient_formset = context['ingredient_formset']
        step_formset = context['step_formset']

        forms_list = [ingredient_formset, step_formset]

        # Act
        response = recipes_handler.forms_valid(forms_list)

        # Assert
        self.assertTrue(response)


    def test_validate_forms_return_false(self):
        # Arrange
        recipe = self.recipe
        data = self.generate_data_for_post_request(1, 1)
        del data['ingredients-0-name']

        request = RequestFactory().post('test/', data=data, formats='multipart')
        context = recipes_handler.fetch_recipe_context_data_for_post_request(recipe, request, RecipeImageForm, self.image)

        ingredient_formset = context['ingredient_formset']
        step_formset = context['step_formset']

        forms_list = [ingredient_formset, step_formset]

        # Act
        response = recipes_handler.forms_valid(forms_list)

        # Assert
        self.assertFalse(response)


    def test_save_recipe_and_forms_success(self):
        # Arrange
        recipe = self.recipe
        data = self.generate_data_for_post_request(ingredients_num=1, steps_num=1)
        request = RequestFactory().post('test/', data=data, formats='multipart')
        context = recipes_handler.fetch_recipe_context_data_for_post_request(recipe, request, RecipeImageForm, self.image)
        # Act
        result = recipes_handler.save_recipe_and_forms(recipe, context)
        # Assert
        self.assertTrue(result)
        self.assertTrue(recipe.ingredients.filter(name='Ingredient 1').exists())
        self.assertTrue(recipe.steps.filter(description='Step 1').exists())
        self.assertTrue(recipe.images.exists())


    def test_save_recipe_and_forms_invalid_ingredient(self):
        # Arrange
        recipe = self.recipe
        data = self.generate_data_for_post_request(ingredients_num=1, steps_num=1)
        del data['ingredients-0-name']  # Remove required field to make form invalid
        request = RequestFactory().post('test/', data=data, formats='multipart')
        context = recipes_handler.fetch_recipe_context_data_for_post_request(recipe, request, RecipeImageForm, self.image)
        # Act
        result = recipes_handler.save_recipe_and_forms(recipe, context)
        # Assert
        self.assertFalse(result)
        self.assertFalse(recipe.ingredients.exists())
        self.assertFalse(recipe.steps.exists())


    def test_save_recipe_and_forms_invalid_step(self):
        # Arrange
        recipe = self.recipe
        data = self.generate_data_for_post_request(ingredients_num=1, steps_num=1)
        del data['steps-0-description']  # Remove required field to make form invalid
        request = RequestFactory().post('test/', data=data, formats='multipart')
        context = recipes_handler.fetch_recipe_context_data_for_post_request(recipe, request, RecipeImageForm, self.image)
        # Act
        result = recipes_handler.save_recipe_and_forms(recipe, context)
        # Assert
        self.assertFalse(result)
        self.assertFalse(recipe.steps.exists())


    def test_save_recipe_and_forms_invalid_image(self):
        # Arrange
        recipe = self.recipe
        data = self.generate_data_for_post_request(ingredients_num=1, steps_num=1)
        # Corrupt the image data to make the image form invalid
        data['picture'] = SimpleUploadedFile('bad.txt', b'notanimage', content_type='text/plain')
        request = RequestFactory().post('test/', data=data, formats='multipart')
        context = recipes_handler.fetch_recipe_context_data_for_post_request(recipe, request, RecipeImageForm, self.image)
        # Act
        result = recipes_handler.save_recipe_and_forms(recipe, context)
        # Assert
        self.assertFalse(result)
        self.assertFalse(recipe.images.filter(picture='bad.txt').exists())


    def test_save_recipe_and_forms_no_image(self):
        # Arrange
        recipe = self.recipe
        data = self.generate_data_for_post_request(ingredients_num=1, steps_num=1)
        # Remove the image from the data
        data.pop('picture', None)
        request = RequestFactory().post('test/', data=data, formats='multipart')
        context = recipes_handler.fetch_recipe_context_data_for_post_request(recipe, request, RecipeImageForm)
        # Act
        result = recipes_handler.save_recipe_and_forms(recipe, context)
        # Assert
        self.assertTrue(result)
        self.assertTrue(recipe.ingredients.filter(name='Ingredient 1').exists())
        self.assertTrue(recipe.steps.filter(description='Step 1').exists())


    def test_save_categories_and_tags_assigns_correctly(self):
        recipe = self.recipe
        # Create additional categories and tags
        category2 = Category.objects.create(name='Second Category')
        tag2 = Tag.objects.create(name='Second Tag')
        # Assign both categories and tags
        category_ids = [self.category.id, category2.id]
        tag_ids = [self.tag.id, tag2.id]
        recipes_handler.save_categories_and_tags(recipe, category_ids, tag_ids)
        # Assert
        self.assertSetEqual(set(recipe.categories.values_list('id', flat=True)), set(category_ids))
        self.assertSetEqual(set(recipe.tags.values_list('id', flat=True)), set(tag_ids))


    def test_save_categories_and_tags_empty_lists(self):
        recipe = self.recipe
        # Assign some categories and tags first
        category2 = Category.objects.create(name='Second Category')
        tag2 = Tag.objects.create(name='Second Tag')
        recipes_handler.save_categories_and_tags(recipe, [self.category.id, category2.id], [self.tag.id, tag2.id])
        # Now remove all
        recipes_handler.save_categories_and_tags(recipe, [], [])
        # Assert
        self.assertEqual(recipe.categories.count(), 0)
        self.assertEqual(recipe.tags.count(), 0)


    def test_save_categories_and_tags_single(self):
        recipe = self.recipe
        recipes_handler.save_categories_and_tags(recipe, [self.category.id], [self.tag.id])
        self.assertEqual(recipe.categories.count(), 1)
        self.assertEqual(recipe.tags.count(), 1)
        self.assertEqual(recipe.categories.first(), self.category)
        self.assertEqual(recipe.tags.first(), self.tag)


    def test_save_categories_and_tags_accepts_string_ids(self):
        recipe = self.recipe
        recipes_handler.save_categories_and_tags(recipe, [str(self.category.id)], [str(self.tag.id)])
        self.assertEqual(recipe.categories.first(), self.category)
        self.assertEqual(recipe.tags.first(), self.tag)




        
