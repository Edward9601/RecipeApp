from django import forms

from ..models.recipe_models import Recipe, RecipeIngredient, RecipeStep, RecipeSubRecipe, RecipeImage
from django.forms import BaseInlineFormSet, ModelForm, inlineformset_factory
from utils.models import ImageHandler

class RecipeFormManager:
    """Manager class to handle formset creation and management"""
    @staticmethod
    def create_formset(model: object, form: ModelForm, data=None, instance=None, extra=0):
        FormSet = inlineformset_factory(
            Recipe, 
            model,
            form=form,
            extra=extra,
            can_delete=True
        )
        return FormSet(data, instance=instance) if data else FormSet()

    @classmethod
    def get_recipe_forms(cls, data=None, instance=None, extra=0):
        """Get all forms needed for recipe creation/editing"""
        return {
            'ingredient_formset': cls.create_ingredient_formset(data, instance, extra),
            'step_formset': cls.create_step_formset(data, instance, extra),
            'image_form': RecipeImageForm(data) if data else RecipeImageForm()
        }
    
    @classmethod
    def get_multiple_choice_field(cls, model: object, reuired:bool=False):
        """Get a multiple choice field for a given model"""
        return forms.ModelMultipleChoiceField(
            queryset=model.objects.all(),
            required=reuired,
            widget=forms.CheckboxSelectMultiple()
        )


class RecipeImageForm(ModelForm):
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
        if picture and picture.name.endswith('.heic'):
            picture = ImageHandler.convert_to_jpeg(picture)
        return picture

class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description']


class RecipeCreateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        # pop extra args before calling super
        self.user = kwargs.pop('user', None)
        extra_forms = kwargs.pop('extra_forms', 1)
        
        # now call super with cleaned kwargs
        super().__init__(*args, **kwargs)
        data = kwargs.pop('data', None)
        files = kwargs.pop('files', None)
        self.ingredients_formset = RecipeFormManager.create_formset(RecipeIngredient, RecipeIngredientForm,data=data, instance=self.instance, extra=extra_forms)
        self.steps_formset = RecipeFormManager.create_formset(RecipeStep, RecipeStepForm,data=data, instance=self.instance, extra=extra_forms)
        self.image_form = RecipeImageForm(data=data,files=files)
        if not self.user:
            raise ValueError("User must be provided to initialize the RecipeCreateForm.")
        self.fields['sub_recipes'] = forms.ModelMultipleChoiceField(
            queryset=Recipe.objects.filter(author=self.user, is_sub_recipe=True),
            required=False,
            widget=forms.CheckboxSelectMultiple(),
            help_text="Select sub-recipes"
        )

    class Meta:
        model = Recipe
        fields = ['title', 'description', 'categories', 'tags'] 

    def is_valid(self) -> bool:
        valid = super().is_valid()
        if not valid:
            return valid
        if self.ingredients_formset.is_valid() and self.steps_formset.is_valid() and self.image_form.is_valid():
            return valid
        else:
            return False
    

    def save(self, commit=True):
        if not self.user:
            raise ValueError("User must be provided to save the SubRecipeForm.")
        instance = super().save(commit=False)
        instance.author = self.user
        instance.is_sub_recipe = False
        if commit:
            instance.save()
            if self.ingredients_formset and self.ingredients_formset.has_changed():
                self.ingredients_formset.instance = instance
                self.ingredients_formset.save()
            if self.steps_formset and self.steps_formset.has_changed():
                self.steps_formset.instance = instance
                self.steps_formset.save()
            if self.image_form and self.image_form.has_changed():
                self.image_form.instance.recipe = instance
                self.image_form.save()
        return instance
    

    def save_recipe_sub_recipe_relationship(self, recipe: Recipe, sub_recipes, intermidiate_table: RecipeSubRecipe) -> None:
        """
        Save the relationship between the recipe and its sub-recipes.
        This method is used to save the relationship between the recipe and its sub-recipes.
        """
        for sub_recipe in sub_recipes:
            intermidiate_table.objects.create(parent_recipe=recipe, sub_recipe=sub_recipe)
    


class RecipeIngredientForm(ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ['name', 'quantity', 'measurement']
        error_messages = {
            'name': {
                'reuired': "Please enter the ingredient name — it can’t be blank."
            }
        }


class RecipeStepForm(ModelForm):
    class Meta:
        model = RecipeStep
        fields = ['description', 'order']
        widgets = {
            'order': forms.HiddenInput()
        }

        error_messages = {
            'description': {
                'required': "Please enter the step description — it can’t be blank."
                }
            }


class SubRecipeCreateForm(ModelForm):
    form_manager = RecipeFormManager()
    class Meta:
        model = Recipe
        fields = ['title', 'description']

    def __init__(self, *args, **kwargs):
        # pop extra args before calling super
        self.user = kwargs.pop('user', None)
        extra_forms = kwargs.pop('extra_forms', 1)
        # now call super with cleaned kwargs
        super().__init__(*args, **kwargs)
        data = kwargs.get('data', None)
        files = kwargs.get('files', None)
        self.ingredient_formset = self.form_manager.create_formset(RecipeIngredient, RecipeIngredientForm,data=data,instance=self.instance, extra=extra_forms)
        self.step_formset = self.form_manager.create_formset(RecipeStep, RecipeStepForm,data=data,instance=self.instance, extra=extra_forms)
        self.image_form = RecipeImageForm(data=data,files=files)
        self.fields['sub_recipes'] = forms.ModelMultipleChoiceField(
            queryset=Recipe.objects.filter(author=self.user,is_sub_recipe=True),
            required=False,
            widget=forms.CheckboxSelectMultiple(),
            help_text="Select sub-recipes"
        )
        if self.instance and self.instance.pk:
            self.fields.get('sub_recipes').queryset = self.fields.get('sub_recipes').queryset.exclude(pk=self.instance.pk)


    def is_valid(self):
        valid = super().is_valid()
        valid = self.ingredient_formset.has_changed() and self.ingredient_formset.is_valid()
        valid = valid and self.step_formset.has_changed() and self.step_formset.is_valid()
        valid = self.image_form.has_changed() and self.image_form.is_valid()
        return valid
    
    def save(self, commit=True):
        if not self.user:
            raise ValueError("User must be provided to save the SubRecipeForm.")
        instance = super().save(commit=False)
        instance.author = self.user
        instance.is_sub_recipe = True
        if commit:
            instance.save()
            if self.ingredient_formset or self.ingredient_formset.has_changed():
                self.ingredient_formset.instance = instance
                self.ingredient_formset.save()
            if self.step_formset or self.step_formset.has_changed():
                self.step_formset.instance = instance
                self.step_formset.save()
            if self.image_form or self.image_form.has_changed():
                self.image_form.instance.recipe = instance
                self.image_form.save()
        return instance
    

    def save_recipe_sub_recipe_relationship(self, recipe: Recipe, sub_recipes, intermidiate_table: RecipeSubRecipe) -> None:
        """
        Save the relationship between the recipe and its sub-recipes.
        This method is used to save the relationship between the recipe and its sub-recipes.
        """
        for sub_recipe in sub_recipes:
            intermidiate_table.objects.create(parent_recipe=recipe, sub_recipe=sub_recipe)


class SubRecipeUpdateForm(ModelForm):
    form_manager = RecipeFormManager()
    class Meta:
        model = Recipe
        fields = ['title', 'description']

    def __init__(self, *args, **kwargs):
        # pop extra args before calling super
        self.user = kwargs.pop('user', None)
        extra_forms = kwargs.pop('extra_forms', 1)
        # now call super with cleaned kwargs
        super().__init__(*args, **kwargs)
        data = kwargs.get('data', None)
        files = kwargs.get('files', None)
        self.ingredient_formset = self.form_manager.create_formset(RecipeIngredient, RecipeIngredientForm,data=data,instance=self.instance, extra=extra_forms)
        self.step_formset = self.form_manager.create_formset(RecipeStep, RecipeStepForm,data=data,instance=self.instance, extra=extra_forms)
        self.image_form = RecipeImageForm(data=data,files=files)
        self.fields['sub_recipes'] = forms.ModelMultipleChoiceField(
            queryset=Recipe.objects.filter(author=self.user,is_sub_recipe=True),
            required=False,
            widget=forms.CheckboxSelectMultiple(),
            help_text="Select sub-recipes"
        )
        if self.instance and self.instance.pk:
            self.fields.get('sub_recipes').queryset = self.fields.get('sub_recipes').queryset.exclude(pk=self.instance.pk)


    def is_valid(self):
        valid = super().is_valid()
        valid = self.image_form.has_changed() and self.image_form.is_valid()
        return valid
    
    def save(self, commit=True):
        if not self.user:
            raise ValueError("User must be provided to save the SubRecipeForm.")
        instance = super().save(commit=False)
        instance.author = self.user
        instance.is_sub_recipe = True
        if commit:
            instance.save()
            # during update ingredients and steps are being updaed through partol views,
            # no need ot validate 
            if self.image_form or self.image_form.has_changed():
                self.image_form.instance.recipe = instance
                self.image_form.save()
        return instance
    

    def save_recipe_sub_recipe_relationship(self, recipe: Recipe, sub_recipes, intermidiate_table: RecipeSubRecipe) -> None:
        """
        Save the relationship between the recipe and its sub-recipes.
        This method is used to save the relationship between the recipe and its sub-recipes.
        """
        for sub_recipe in sub_recipes:
            intermidiate_table.objects.create(parent_recipe=recipe, sub_recipe=sub_recipe)

    def update_recipe_sub_recipe_relationship(self, recipe: Recipe,new_recipes_to_add, current_sub_recipes, recipe_sub_recipe_model: RecipeSubRecipe):
        """
        Update the relationship between the recipe and its sub-recipes.
        This method is used to update the relationship between the recipe and its sub-recipes.
        """

        sub_recipes_to_add = new_recipes_to_add - current_sub_recipes
        to_remove = current_sub_recipes - new_recipes_to_add
        try:
            if to_remove:
                recipe_sub_recipe_model.objects.filter(recipe=recipe, sub_recipe__in=to_remove).delete()
            if sub_recipes_to_add:
                recipe_sub_recipe_model.objects.bulk_create([RecipeSubRecipe(parent_recipe=recipe, sub_recipe=sub_recipe) 
                                                                    for sub_recipe 
                                                                    in sub_recipes_to_add])
        except Exception as e:
            return (False, str(e))
        return (True, '')

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



