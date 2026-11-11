from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from recipes.models.recipe_models import Recipe


class RecipeAuthorizationTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username='owner', password='pass1234')
        self.other_user = get_user_model().objects.create_user(username='other', password='pass1234')
        self.recipe = Recipe.objects.create(title='Owner recipe', author=self.owner, is_sub_recipe=False)
        self.sub_recipe = Recipe.objects.create(title='Owner sub-recipe', author=self.owner, is_sub_recipe=True)

    def test_recipe_update_and_ingredient_routes_are_owner_scoped(self):
        self.client.force_login(self.other_user)

        recipe_update_response = self.client.get(reverse('recipes:update', args=[self.recipe.pk]))
        self.assertEqual(recipe_update_response.status_code, 404)

        ingredients_response = self.client.get(reverse('recipes:fetch_recipe_ingredients', args=[self.recipe.pk]))
        self.assertEqual(ingredients_response.status_code, 404)

    def test_sub_recipe_update_and_delete_are_owner_scoped(self):
        self.client.force_login(self.other_user)

        sub_update_response = self.client.get(reverse('recipes:update_sub_recipe', args=[self.sub_recipe.pk]))
        self.assertEqual(sub_update_response.status_code, 404)

        delete_response = self.client.post(reverse('recipes:delete_sub_recipe', args=[self.sub_recipe.pk]))
        self.assertEqual(delete_response.status_code, 404)
