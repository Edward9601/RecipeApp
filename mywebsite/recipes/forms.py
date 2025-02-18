from django import forms
from .models import Recipe, Ingredient, Step


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'picture', 'note']


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'quantity', 'measurement'] 


class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ['description', 'order']

class SubRecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'note']
