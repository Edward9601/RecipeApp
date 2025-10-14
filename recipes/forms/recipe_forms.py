from django import forms

from ..models.recipe_models import Recipe, RecipeIngredient, RecipeStep, Tag, Category, RecipeImage
from django.forms import BaseInlineFormSet, inlineformset_factory
from utils.models import ImageHandler

class RecipeFormManager:
    """Manager class to handle formset creation and management"""
    @staticmethod
    def create_ingredient_formset(data=None, instance=None, extra=0):
        IngredientFormSet = inlineformset_factory(
            Recipe, 
            RecipeIngredient,
            form=RecipeIngredientForm,
            extra=extra,
            can_delete=True
        )
        return IngredientFormSet(data, instance=instance) if data else IngredientFormSet()

    @staticmethod
    def create_step_formset(data=None, instance=None, extra=0):
        StepFormSet = inlineformset_factory(
            Recipe, 
            RecipeStep,
            form=RecipeStepForm,
            extra=extra,
            can_delete=True
        )
        return StepFormSet(data, instance=instance) if data else StepFormSet()

    @classmethod
    def get_recipe_forms(cls, data=None, instance=None, extra=0):
        """Get all forms needed for recipe creation/editing"""
        return {
            'ingredient_formset': cls.create_ingredient_formset(data, instance, extra),
            'step_formset': cls.create_step_formset(data, instance, extra),
            'image_form': RecipeImageForm(data) if data else RecipeImageForm()
        }


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

    sub_recipes = forms.ModelMultipleChoiceField(
        queryset=Recipe.objects.filter(is_sub_recipe=True),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        help_text="Select sub-recipes"
    )

    class Meta:
        model = Recipe
        fields = ['title', 'description', 'parent_recipe', 'categories', 'tags'] 
        widgets = {
            'parent_recipe': forms.CheckboxSelectMultiple()
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
    form_manager = RecipeFormManager()
    class Meta:
        model = Recipe
        fields = ['title']

    def __init__(self, *args, **kwargs):
        # pop extra args before calling super
        self.user = kwargs.pop('user', None)
        extra_forms = kwargs.pop('extra_forms', 1)
        data = kwargs.get('data', None)
        # now call super with cleaned kwargs
        super().__init__(*args, **kwargs)
        self.ingredient_formset = self.form_manager.create_ingredient_formset(data=data,instance=self.instance, extra=extra_forms)
        self.step_formset = self.form_manager.create_step_formset(data=data,instance=self.instance, extra=extra_forms)


    def is_valid(self):
        valid = super().is_valid()
        valid = valid and self.ingredient_formset.is_valid() and self.step_formset.is_valid()
        return valid
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.author = self.user
        instance.is_sub_recipe = True
        if commit:
            instance.save()
            self.ingredient_formset.instance = instance
            self.ingredient_formset.save()
            self.step_formset.instance = instance
            self.step_formset.save()
        return instance


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



