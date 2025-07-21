from recipes.forms.recipe_forms import fetch_ingredients_and_steps_formsets, RecipeImageForm, RecipeCreateForm
from recipes.models.recipe_models import Recipe, Category, Tag, RecipeSubRecipe
from utils.models import ImageHandler as image_handler

from django.core.handlers.wsgi import WSGIRequest


from django.core.cache import cache

import os



def fetch_recipe_context_data_for_post_request(recipe: Recipe, request: WSGIRequest, image_form: RecipeImageForm, image_instance=None) -> dict:
    """
    Populates the context data for POST requests.
    This function is used to handle form submissions and populate the context with form data.
    """
    # Fetch the formsets for ingredients and steps
    ingredient_formset, steps_formset = fetch_ingredients_and_steps_formsets()
    
    # For POST requests, we might not have a recipe instance yet, so we pass None
    # The formsets will handle this properly
    context = {
        'ingredient_formset': ingredient_formset(request.POST,
                                                instance=recipe,
                                                prefix='ingredients'),
        'step_formset': steps_formset(request.POST,
                                      instance=recipe,
                                      prefix='steps'),
    }
    if request.FILES:
        # If there are files in the request, ensure the image form is included
        context['image_form'] = image_form(request.POST,
                                           request.FILES,
                                           instance=image_instance)
    return context


def fetch_recipe_context_data_for_get_request(recipe: Recipe, image_form: RecipeImageForm, image_instance=None, extra_forms=0) -> dict:
    """
    Populates the context data for POST requests.
    This function is used to handle form submissions and populate the context with form data.
    """
    # Fetch the formsets for ingredients and steps
    ingredient_formset, step_formset = fetch_ingredients_and_steps_formsets(extra_forms)
    initial_data = [{"order": 1}]
    context = {
        'ingredient_formset': ingredient_formset(instance=recipe, prefix='ingredients'),
        'step_formset': step_formset(instance=recipe, prefix='steps', initial=initial_data),
        'image_form': image_form(instance=image_instance),
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
        'form': RecipeCreateForm(instance=recipe),
    }
    return context


def save_valid_forms(recipe: Recipe, form_list) -> bool:
        """
        Save the image forms and associate them with the recipe instance.
        This method is used to save the forms that are valid and associate them with the recipe instance
        """
        for form in form_list:
            # Associate parent instance before saving
            form.instance = recipe
            form.save()

def save_image_form(recipe: Recipe, image_form: RecipeImageForm) -> None:
    """
    Save the image form and associate it with the recipe instance.
    This method is used to save the image form that is valid and associate it with the recipe instance.
    """
    image_form.instance.recipe = recipe
    # Only rename if both recipe and picture are set
    if image_form.instance.picture and image_form.instance.recipe:
        orig = image_form.instance.picture
        ext = os.path.splitext(orig.name)[1]
        base_name = image_handler.slugify_name(recipe.title)
        new_name = f'{base_name}{ext}'
        image_form.instance.picture.name = new_name
    image_form.save()

def save_recipe_sub_recipe_relationship(recipe: Recipe, sub_recipes, intermidiate_table: RecipeSubRecipe) -> None:
    """
    Save the relationship between the recipe and its sub-recipes.
    This method is used to save the relationship between the recipe and its sub-recipes.
    """
    for sub_recipe in sub_recipes:
        intermidiate_table.objects.create(recipe=recipe, sub_recipe=sub_recipe)


def validate_forms(forms) -> bool:
    """
    Check if the ingredient and step formsets are valid.
    If an image form is provided, it also checks if the image form is valid.
    """
    if all(form.is_valid() for form in forms):
        return True
    return False
    

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

def save_recipe_and_forms(recipe: Recipe, context: dict) -> bool:
    """
    Save the recipe and its associated forms.
    This method is used to save the recipe and its associated forms.
    """
    

    ingredient_formset = context['ingredient_formset']
    step_formset = context['step_formset']
    image_form = context.get('image_from', None)

    forms_list = [ingredient_formset, step_formset]
    if validate_forms(forms_list):
        # Save the recipe first so it has an ID for the formsets
        recipe.save()
        
        if image_form:
            if image_form.is_valid():
                    # Save the image form if it is valid
                save_image_form(recipe, image_form)
            else:
                return  False
                
        save_valid_forms(recipe, forms_list)
        return True
    return False

def save_categories_and_tags(recipe: Recipe, category_list, tag_list):
    """
    Save the categories and tags for the recipe.
    This method is used to save the categories and tags for the recipe.
    """
    category_ids = [int(cat_id) for cat_id in category_list]
    tag_ids = [int(tag_id) for tag_id in tag_list]

    recipe.categories.set(category_ids)
    
    recipe.tags.set(tag_ids)


def update_recipe_sub_recipe_relationship(recipe: Recipe,new_recipes_to_add, current_sub_recipes, recipe_sub_recipe_model: RecipeSubRecipe):
    """
    Update the relationship between the recipe and its sub-recipes.
    This method is used to update the relationship between the recipe and its sub-recipes.
    """

    sub_recipes_to_add = new_recipes_to_add - current_sub_recipes
    to_remove = current_sub_recipes - new_recipes_to_add
    try:
        if to_remove:
            recipe_sub_recipe_model.objects.filter(recipe=recipe, sub_recipe__in=to_remove).delete()
        if sub_recipes_to_add:
            recipe_sub_recipe_model.objects.bulk_create([RecipeSubRecipe(recipe=recipe, sub_recipe=sub_recipe) 
                                                                for sub_recipe 
                                                                in sub_recipes_to_add])
    except Exception as e:
        return (False, str(e))
    return (True, '')

def create_recipe_sub_recipe_relationship(recipe: Recipe, sub_recipes):
    """
    Create the relationship between the recipe and its sub-recipes.
    This method is used to create the relationship between the recipe and its sub-recipes.
    """
    try:
        for sub_recipe in sub_recipes:
            RecipeSubRecipe.objects.create(recipe=recipe, sub_recipe=sub_recipe)
    except Exception as e:
        return (False, str(e))
    return (True, '')

   
