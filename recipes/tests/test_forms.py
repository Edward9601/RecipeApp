# """Revisit tests, rewrite and complete them."""



# from django.test import TestCase
# from django.core.files.uploadedfile import SimpleUploadedFile
# from django.contrib.auth.models import User
# from ..forms.recipe_forms import RecipeHomeForm, RecipeIngredientForm, RecipeStepForm
# from ..forms.sub_recipe_forms import SubRecipeForm, SubRecipeIngredientForm, SubRecipeStepForm
# from ..models.recipe_models import Recipe
# from ..models.sub_recipe_models import SubRecipe

# class RecipeFormTests(TestCase):
#     def setUp(self):
#         # Create a test user
#         self.user = User.objects.create_user(
#             username='testuser',
#             password='testpass123'
#         )
        
#         # Create a test image
#         self.test_image = SimpleUploadedFile(
#             name='test_image.jpg',
#             content=b'',  # Empty content for testing
#             content_type='image/jpeg'
#         )

#     def test_recipe_form_valid_data(self):
#         """Test RecipeForm with valid data"""
#         form_data = {
#             'title': 'Test Recipe',
#             'description': 'This is a test recipe description',
#             'picture': self.test_image
#         }
#         form = RecipeHomeForm(data=form_data)
#         self.assertTrue(form.is_valid())

#     def test_recipe_form_invalid_data(self):
#         """Test RecipeForm with invalid data"""
#         form_data = {
#             'title': '',  # Empty title should be invalid
#             'description': 'This is a test recipe description'
#         }
#         form = RecipeHomeForm(data=form_data)
#         self.assertFalse(form.is_valid())
#         self.assertIn('title', form.errors)

#     def test_recipe_form_without_picture(self):
#         """Test RecipeForm without picture (should be valid as picture is optional)"""
#         form_data = {
#             'title': 'Test Recipe',
#             'description': 'This is a test recipe description'
#         }
#         form = RecipeHomeForm(data=form_data)
#         self.assertTrue(form.is_valid())

# class RecipeIngredientFormTests(TestCase):
#     def test_ingredient_form_valid_data(self):
#         """Test RecipeIngredientForm with valid data"""
#         form_data = {
#             'name': 'Salt',
#             'quantity': '1',
#             'measurement': 'tsp'
#         }
#         form = RecipeIngredientForm(data=form_data)
#         self.assertTrue(form.is_valid())

#     def test_ingredient_form_without_measurement(self):
#         """Test RecipeIngredientForm without measurement (should be valid)"""
#         form_data = {
#             'name': 'Eggs',
#             'quantity': '2'
#         }
#         form = RecipeIngredientForm(data=form_data)
#         self.assertTrue(form.is_valid())

#     def test_ingredient_form_invalid_data(self):
#         """Test RecipeIngredientForm with invalid data"""
#         form_data = {
#             'name': '',  # Empty name should be invalid
#             'quantity': '1',
#             'measurement': 'tsp'
#         }
#         form = RecipeIngredientForm(data=form_data)
#         self.assertFalse(form.is_valid())
#         self.assertIn('name', form.errors)

# class RecipeStepFormTests(TestCase):
#     def test_step_form_valid_data(self):
#         """Test RecipeStepForm with valid data"""
#         form_data = {
#             'description': 'Mix all ingredients together',
#             'order': 1
#         }
#         form = RecipeStepForm(data=form_data)
#         self.assertTrue(form.is_valid())

#     def test_step_form_invalid_data(self):
#         """Test RecipeStepForm with invalid data"""
#         form_data = {
#             'description': '',  # Empty description should be invalid
#             'order': 1
#         }
#         form = RecipeStepForm(data=form_data)
#         self.assertFalse(form.is_valid())
#         self.assertIn('description', form.errors)

# class SubRecipeFormTests(TestCase):
#     def test_sub_recipe_form_valid_data(self):
#         """Test SubRecipeForm with valid data"""
#         form_data = {
#             'title': 'Test Sub Recipe',
#             'note': 'This is a test sub recipe note'
#         }
#         form = SubRecipeForm(data=form_data)
#         self.assertTrue(form.is_valid())

#     def test_sub_recipe_form_invalid_data(self):
#         """Test SubRecipeForm with invalid data"""
#         form_data = {
#             'title': '',  # Empty title should be invalid
#             'note': 'This is a test sub recipe note'
#         }
#         form = SubRecipeForm(data=form_data)
#         self.assertFalse(form.is_valid())
#         self.assertIn('title', form.errors)

# class SubRecipeIngredientFormTests(TestCase):
#     def test_sub_recipe_ingredient_form_valid_data(self):
#         """Test SubRecipeIngredientForm with valid data"""
#         form_data = {
#             'name': 'Flour',
#             'quantity': '2',
#             'measurement': 'cup',
#         }
#         form = SubRecipeIngredientForm(data=form_data)
#         self.assertTrue(form.is_valid())

#     def test_sub_recipe_ingredient_form_without_measurement(self):
#         """Test SubRecipeIngredientForm without measurement (should be valid)"""
#         form_data = {
#             'name': 'Eggs',
#             'quantity': '3'
#         }
#         form = SubRecipeIngredientForm(data=form_data)
#         self.assertTrue(form.is_valid())

#     def test_sub_recipe_ingredient_form_invalid_data(self):
#         """Test SubRecipeIngredientForm with invalid data"""
#         form_data = {
#             'name': '',  # Empty name should be invalid
#             'quantity': '2',
#             'measurement': 'cups'
#         }
#         form = SubRecipeIngredientForm(data=form_data)
#         self.assertFalse(form.is_valid())
#         self.assertIn('name', form.errors)

# class SubRecipeStepFormTests(TestCase):
#     def test_sub_recipe_step_form_valid_data(self):
#         """Test SubRecipeStepForm with valid data"""
#         form_data = {
#             'description': 'Mix dry ingredients',
#             'order': 1
#         }
#         form = SubRecipeStepForm(data=form_data)
#         self.assertTrue(form.is_valid())

#     def test_sub_recipe_step_form_invalid_data(self):
#         """Test SubRecipeStepForm with invalid data"""
#         form_data = {
#             'description': '',  # Empty description should be invalid
#             'order': 1
#         }
#         form = SubRecipeStepForm(data=form_data)
#         self.assertFalse(form.is_valid())
#         self.assertIn('description', form.errors) 