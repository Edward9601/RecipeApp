from ..models.recipe_models import Recipe, RecipeSubRecipe, RecipeStep, RecipeIngredient
from ..models.sub_recipe_models import SubRecipe
from django.views.generic import CreateView
from ..forms.recipe_forms import RecipeIngredientForm, RecipeStepForm, RecipeForm
from ..forms.sub_recipe_forms import SubRecipeForm
from django.forms import inlineformset_factory
from django import forms
from helpers.mixins import UsersAndGuestsAuth


class BaseRecipeView(UsersAndGuestsAuth):
    """
    Base view for recipes to extend
    """
    model = Recipe
    form_class = RecipeForm
    intermediate_table = RecipeSubRecipe


class BaseViewForDataUpdate(BaseRecipeView):
    """
    Base view to handle create and update operation on recipes.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_formset_count = 0
        initial_data = [{}]
        if isinstance(self, CreateView):
            extra_formset_count = 1
            initial_data = [{"order": 1}]
  

        ingredient_form_set = inlineformset_factory(Recipe, RecipeIngredient, form=RecipeIngredientForm,
                                                    extra=extra_formset_count,
                                                    can_delete=True)
        step_form_set = inlineformset_factory(Recipe, RecipeStep, form=RecipeStepForm, extra=extra_formset_count,
                                              can_delete=True)
        if self.request.POST:
            context['ingredient_formset'] = ingredient_form_set(self.request.POST, instance=self.object,
                                                                prefix='ingredients')
            context['step_formset'] = step_form_set(self.request.POST, instance=self.object, prefix='steps')
        else:
            context['ingredient_formset'] = ingredient_form_set(instance=self.object, prefix='ingredients')
            context['step_formset'] = step_form_set(instance=self.object, prefix='steps', initial=initial_data)
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['sub_recipes'] = forms.ModelMultipleChoiceField(
            queryset=SubRecipe.objects.all(),
            widget=forms.CheckboxSelectMultiple(attrs={'class': 'no-border-checkbox'}),  # Ensures correct rendering
            required=False  # Optional selection
        )
        return form

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save(commit=False)
        # Ingredient formset handling
        context = self.get_context_data()
        ingredient_formset = context['ingredient_formset']
        step_formset = context['step_formset']

        if ingredient_formset.is_valid() and step_formset.is_valid():
            self.object.save()
            ingredient_formset.save()
            step_formset.save()
        else:
            response = super().form_invalid(form)
            return response

        return self.object
    

class BaseSubRecipeView():
        model = SubRecipe
        form_class = SubRecipeForm