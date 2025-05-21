from django import forms

from ..models.recipe_models import Recipe, RecipeIngredient, RecipeStep


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'picture']  # TODO add 'note' when will be needed


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ['name', 'quantity', 'measurement']


class RecipeStepForm(forms.ModelForm):
    class Meta:
        model = RecipeStep
        fields = ['description', 'order']
        widgets = {
            'order': forms.HiddenInput()
        }