from django import forms

from ..models.recipe_models import Recipe, RecipeIngredient, RecipeStep, Tag, Category, RecipeImage
from django.forms import BaseInlineFormSet, inlineformset_factory
from utils.models import ImageHandler

class RecipeImageForm(forms.ModelForm):
    class Meta:
        model = RecipeImage
        fields = ['picture']

    def save(self, commit=True): # Currently being triggerend even if image is not submitted
        instance = super().save(commit=False)
        if commit:
            instance.save()
            # Create thumbnail after saving the image
            if instance.picture:
                instance.create_thumbnail(instance.thumbnail_folder, instance.picture.name, size=(600, 600))
        return instance
    

    def clean_picture(self):
        picture = self.cleaned_data.get('picture')
        if picture.name.endswith('.heic'):
            picture = ImageHandler.convert_to_jpeg(picture)
        return picture

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description']


class RecipeCreateForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        help_text="Select categories"
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        help_text="Select tags"
    )

    class Meta:
        model = Recipe
        fields = ['title', 'description', 'parent_recipe', 'categories', 'tags', 'is_sub_recipe'] 
        widgets = {
            'parent_recipe': forms.CheckboxSelectMultiple(),
            'is_sub_recipe': forms.CheckboxInput(),
        }


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


class SubRecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title']

def fetch_ingredients_form(extra_forms:int =0) -> BaseInlineFormSet:
    """
    Fetch the ingredients form for the recipe.
    """
    IngredientFormSet = inlineformset_factory(Recipe, RecipeIngredient,extra=extra_forms, form=RecipeIngredientForm, can_delete=True)
    return IngredientFormSet

def fetch_steps_form(extra_forms:int =0) -> dict:
    """
    Fetch the steps form for the recipe.
    """
    StepsFormSet = inlineformset_factory(Recipe, RecipeStep,extra=extra_forms, form=RecipeStepForm, can_delete=True)
    return StepsFormSet


def fetch_ingredients_and_steps_formsets(extra_forms:int =0):
    """
    Returns the ingredient and step formsets for a recipe.
    """    
    IngredientFormSet = fetch_ingredients_form(extra_forms)
    StepsFormSet = fetch_steps_form(extra_forms)
    return IngredientFormSet, StepsFormSet

