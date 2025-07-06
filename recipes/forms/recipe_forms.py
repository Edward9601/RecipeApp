from django import forms

from ..models.recipe_models import Recipe, RecipeIngredient, RecipeStep, Tag, Category, RecipeImage
from django.forms import inlineformset_factory
import os

class RecipeImageForm(forms.ModelForm):
    class Meta:
        model = RecipeImage
        fields = ['picture']

    def save(self, commit=True): # Currently being triggerend even if image is not submitted
        instance = super().save(commit=False)
        print('Saving RecipeImageForm with instance:', instance)
        if commit:
            instance.save()
            print('RecipeImageForm saved with instance:', instance)
            # Create thumbnail after saving the image
            if instance.picture:
                instance.create_thumbnail(instance.thumbnail_folder, instance.picture.name, size=(600, 600))
        return instance

class RecipeHomeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description']


class RecipeCreateForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        help_text="Select categories"  # Add help text for debugging
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        help_text="Select tags"  # Add help text for debugging
    )

    class Meta:
        model = Recipe
        fields = ['title', 'description', 'sub_recipes', 'categories', 'tags'] 
        widgets = {
            'sub_recipes': forms.CheckboxSelectMultiple(),
        }

        
class RecipeDetailForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'note']


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


def fetch_ingredients_and_steps_formsets(extra_forms=0):
    """
    Returns the ingredient and step formsets for a given recipe instance.
    """    
    IngredientFormSet = inlineformset_factory(Recipe, RecipeIngredient,extra=extra_forms, form=RecipeIngredientForm, can_delete=True)
    StepsFormSet = inlineformset_factory(Recipe, RecipeStep,extra=extra_forms, form=RecipeStepForm, can_delete=True)
    return IngredientFormSet, StepsFormSet

