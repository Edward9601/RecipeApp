from django import forms

from ..models.recipe_models import Recipe, RecipeIngredient, RecipeStep, Tag, Category, RecipeImage
from django.forms import inlineformset_factory
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


def fetch_ingredients_and_steps_formsets(extra_forms:int =0):
    """
    Returns the ingredient and step formsets for a recipe.
    """    
    IngredientFormSet = inlineformset_factory(Recipe, RecipeIngredient,extra=extra_forms, form=RecipeIngredientForm, can_delete=True)
    StepsFormSet = inlineformset_factory(Recipe, RecipeStep,extra=extra_forms, form=RecipeStepForm, can_delete=True)
    return IngredientFormSet, StepsFormSet

