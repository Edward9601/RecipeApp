from django import forms
from .models import Recipe, RecipeIngredient, RecipeStep, SubRecipe, SubRecipeIngredient, SubRecipeStep


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'picture', 'note']


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ['name', 'quantity', 'measurement'] 


class RecipeStepForm(forms.ModelForm):
    class Meta:
        model = RecipeStep
        fields = ['description', 'order']

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
