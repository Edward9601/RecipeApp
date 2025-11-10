from recipes.forms import recipe_forms 
from recipes.models.recipe_models import Recipe, Category, Tag, RecipeSubRecipe
from utils.models import ImageHandler as image_handler

from django.core.handlers.wsgi import WSGIRequest

from django.core.cache import cache

import os
def fetch_partial_recipe_context_data_for_get(recipe: Recipe, partial_type: str, extra_forms:int =0) -> dict:
    """
    Fetch the partial context data for the recipe.
    This function is used to fetch the partial context data for the recipe.
    """
    context = {}
    if partial_type == 'ingredients':
        ingredients_formset = recipe_forms.fetch_ingredients_form(extra_forms)
        return {
            'ingredients_formset': ingredients_formset(instance=recipe, prefix='ingredients'),
            'recipe': recipe if recipe else None,
        }
    elif partial_type == 'steps':
        steps_formset = recipe_forms.fetch_steps_form(extra_forms)
        
        # Set initial order to 1, ris field is hidden for better user expericence so first step should have order 1
        initial_data = [{"order": 1}]
        return {
            'steps_formset': steps_formset(instance=recipe, prefix='steps', initial=initial_data), 
            'recipe': recipe if recipe else None,
        }
    return context


def fetch_partial_form_for_post_request(request: WSGIRequest, partial_type: str, recipe: Recipe = None) -> dict:
    """
    Fetch the ingredients form for the recipe.
    """
    if partial_type == 'ingredients':
        ingredietns_formset= recipe_forms.fetch_ingredients_form()
        return {
            'ingredients_formset': ingredietns_formset(request.POST, instance=recipe, prefix='ingredients'),
            'recipe': recipe,
        }
    else:
        steps_formset= recipe_forms.fetch_steps_form()
        return {
            'steps_formset': steps_formset(request.POST, instance=recipe, prefix='steps'),
            'recipe': recipe,
        }



# TODO: Implement caching Manager or something to centrilize caching logic
def get_cached_object(key: str) -> object:
    """
    Retrieves an object from the cache using the provided key.
    If the object is not found in the cache, it returns None.
    """
    return cache.get(key)

def set_cached_object(key: str, value, timeout=None) -> tuple:
    """
    Sets an object in the cache with the provided key and value.
    If a timeout is specified, it will be used; otherwise, the default timeout will be used.
    """
    try:
        cache.set(key, value, timeout)
    except Exception as e:
        return (False, str(e))
    return (True, '')



def invalidate_recipe_cache(recipe_id=None) -> dict:
    """
    Invalidates the recipe cache.
    """
    try:
        if recipe_id:
            cache.delete(recipe_id)
        cache.delete('recipe_list_queryset')
    except Exception as e:
        return {'status': 'Cache invalidation failed', 'error': str(e)}
    return {'status': 'Cache invalidated'}