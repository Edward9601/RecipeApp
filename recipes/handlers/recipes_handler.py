from recipes.forms.recipe_forms import fetch_ingredients_and_steps_formsets, RecipeImageForm
from recipes.models.recipe_models import Recipe, RecipeIngredient, RecipeStep, Category, Tag

import os
def populate_context_data_for_post(instance: Recipe, image_instance=None):
    """
    Populates the context data for POST requests.
    This function is used to handle form submissions and populate the context with form data.
    """
    # Fetch the formsets for ingredients and steps
    ingredient_formset, steps_formset = fetch_ingredients_and_steps_formsets()
    context = {
        'ingredient_formset': ingredient_formset(instance.request.POST,
                                                instance=instance.object,
                                                prefix='ingredients'),
        'step_formset': steps_formset(instance.request.POST,
                                      instance=instance.object,
                                      prefix='steps'),
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
    }
    if instance.request.FILES:
        # If there are files in the request, ensure the image form is included
        context['image_from'] = instance.image_form(instance.request.POST,
                                                    instance.request.FILES,
                                                    instance=image_instance)
    return context


def populate_context_data_for_get(instance: Recipe, image_instance=None):
    """
    Populates the context data for POST requests.
    This function is used to handle form submissions and populate the context with form data.
    """
    # Fetch the formsets for ingredients and steps
    ingredient_formset, steps_formset = fetch_ingredients_and_steps_formsets()
    context = {
        'ingredient_formset': ingredient_formset(instance=instance.object, prefix='ingredients'),
        'step_formset': steps_formset(instance=instance.object, prefix='steps'),
        'image_from': instance.image_form(instance=image_instance),
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
    }
    return context


def save_valid_forms(recipe_object: Recipe, form_list):
        """
        Save the image forms and associate them with the recipe instance.
        This method is used to save the forms that are valid and associate them with the recipe instance
        """
        for form in form_list:
            # Associate parent instance before saving
            form.instance = recipe_object
            form.save()

def save_image_form(recipe_object: Recipe, image_form: RecipeImageForm):
    """
    Save the image form and associate it with the recipe instance.
    This method is used to save the image form that is valid and associate it with the recipe instance.
    """
    image_form.instance.recipe = recipe_object
    # Only rename if both recipe and picture are set
    if image_form.instance.picture and image_form.instance.recipe:
        orig = image_form.instance.picture
        ext = os.path.splitext(orig.name)[1]
        base_name = image_form.instance.slugify(recipe_object.title)
        new_name = f'{base_name}{ext}'
        image_form.instance.picture.name = new_name
    image_form.save()



def are_forms_valid(forms):
    """
    Check if the ingredient and step formsets are valid.
    If an image form is provided, it also checks if the image form is valid.
    """
    if all(form.is_valid() for form in forms):
        return True
    return False
    