from django import forms

from ..models.recipe_models import Recipe, RecipeIngredient, RecipeStep, Tag, Category, RecipeImage


class RecipeImageForm(forms.ModelForm):
    class Meta:
        model = RecipeImage
        fields = ['picture']

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