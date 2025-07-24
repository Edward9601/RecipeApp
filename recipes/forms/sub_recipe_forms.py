from django import forms
from django.forms import inlineformset_factory
from ..models.sub_recipe_models import SubRecipe, SubRecipeIngredient, SubRecipeStep

class SubRecipeForm(forms.ModelForm):
    class Meta:
        model = SubRecipe
        fields = ['title']


class SubRecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = SubRecipeIngredient
        fields = ['name', 'quantity', 'measurement']


class SubRecipeStepForm(forms.ModelForm):
    class Meta:
        model = SubRecipeStep
        fields = ['description', 'order']
        widgets = {
            'order': forms.HiddenInput()
        }



def fetch_ingredients_and_steps_formsets_for_sub_recipe(extra_forms: int = 0):
    """
    Returns the ingredient and step formsets for a sub recipe.
    """    
    SubIngredientFormSet = inlineformset_factory(SubRecipe, SubRecipeIngredient,extra=extra_forms, form=SubRecipeIngredientForm, can_delete=True)
    SubStepsFormSet = inlineformset_factory(SubRecipe, SubRecipeStep,extra=extra_forms, form=SubRecipeStepForm, can_delete=True)
    return SubIngredientFormSet, SubStepsFormSet