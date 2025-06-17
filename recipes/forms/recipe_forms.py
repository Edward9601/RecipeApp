from django import forms

from ..models.recipe_models import Recipe, RecipeIngredient, RecipeStep, Tag, Category


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'picture']  # TODO add 'note' when will be needed


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
        fields = ['title', 'description', 'picture', 'sub_recipes', 'categories', 'tags']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("Form initialized with data:", self.data if hasattr(self, 'data') else "No data")

        
class RecipeDetailForm(forms.ModelForm):
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
        widgets = {
            'order': forms.HiddenInput()
        }