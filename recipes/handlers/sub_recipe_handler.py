from ..models.sub_recipe_models import SubRecipe

from django.core.handlers.wsgi import WSGIRequest

from ..forms.sub_recipe_forms import fetch_ingredients_and_steps_formsets_for_sub_recipe, SubRecipeForm

def fetch_sub_recipe_context_data_for_post_request(sub_recipe: SubRecipe, request: WSGIRequest) -> dict:
    """
    Populates the context data for POST requests.
    This function is used to handle form submissions and populate the context with form data.
    """
    # Fetch the formsets for ingredients and steps
    ingredient_formset, steps_formset = fetch_ingredients_and_steps_formsets_for_sub_recipe()
    
    # For POST requests, we might not have a recipe instance yet, so we pass None
    # The formsets will handle this properly
    context = {
        'ingredient_formset': ingredient_formset(request.POST,
                                                instance=sub_recipe,
                                                prefix='ingredients'),
        'step_formset': steps_formset(request.POST,
                                      instance=sub_recipe,
                                      prefix='steps'),
    }
    return context


def fetch_sub_recipe_context_data_for_get_request(recipe: SubRecipe, extra_forms=0) -> dict:
    """
    Populates the context data for POST requests.
    This function is used to handle form submissions and populate the context with form data.
    """
    # Fetch the formsets for ingredients and steps
    ingredient_formset, step_formset = fetch_ingredients_and_steps_formsets_for_sub_recipe(extra_forms)
    initial_data = [{"order": 1}]
    context = {
        'ingredient_formset': ingredient_formset(instance=recipe, prefix='ingredients'),
        'step_formset': step_formset(instance=recipe, prefix='steps', initial=initial_data),
        'form': SubRecipeForm(instance=recipe),
    }
    return context

def validate_forms(forms_list) -> bool:
    if all(form.is_valid() for form in forms_list):
        return True
    return False