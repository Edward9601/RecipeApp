from django import forms

from ..models.sub_recipe_models import SubRecipe, SubRecipeIngredient, SubRecipeStep

class SubRecipeForm(forms.ModelForm):
    class Meta:
        model = SubRecipe
        fields = ['title', 'note']


class SubRecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = SubRecipeIngredient
        fields = ['name', 'quantity', 'measurement']


class SubRecipeStepForm(forms.ModelForm):
    class Meta:
        model = SubRecipeStep
        fields = ['description', 'order']