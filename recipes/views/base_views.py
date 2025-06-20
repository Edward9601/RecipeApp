from ..models.recipe_models import Recipe, RecipeSubRecipe, RecipeStep, RecipeIngredient, Category, Tag
from ..models.sub_recipe_models import SubRecipe
from django.views.generic import CreateView
from ..forms.recipe_forms import RecipeIngredientForm, RecipeStepForm, RecipeForm, RecipeCreateForm
from ..forms.sub_recipe_forms import SubRecipeForm
from django.forms import inlineformset_factory
from django import forms


class BaseRecipeView():
    """
    Base view for recipes to extend
    """
    model = Recipe
    form_class = RecipeForm
    intermediate_table = RecipeSubRecipe


class BaseViewForDataUpdate(BaseRecipeView): # TODO: Refactor this to be more generic
    """
    Base view to handle create and update operation on recipes.
    """
    form_class = RecipeCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_formset_count = 0
        initial_data = [{}]
        
        if isinstance(self, CreateView):
            extra_formset_count = 1
            initial_data = [{"order": 1}]
  
        ingredient_form_set = inlineformset_factory(Recipe, RecipeIngredient, form=RecipeIngredientForm,
                                                    extra=extra_formset_count, can_delete=True)
        step_form_set = inlineformset_factory(Recipe, RecipeStep, form=RecipeStepForm,
                                              extra=extra_formset_count, can_delete=True)
        if self.request.POST:
            context['ingredient_formset'] = ingredient_form_set(self.request.POST, instance=self.object,
                                                                prefix='ingredients')
            context['step_formset'] = step_form_set(self.request.POST, instance=self.object, prefix='steps')
        else:
            context['ingredient_formset'] = ingredient_form_set(instance=self.object, prefix='ingredients')
            context['step_formset'] = step_form_set(instance=self.object, prefix='steps', initial=initial_data)

        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save(commit=False)

        context = self.get_context_data()
        ingredient_formset = context['ingredient_formset']
        step_formset = context['step_formset']

        if ingredient_formset.is_valid() and step_formset.is_valid():
            self.object.save()

            # Associate parent instance before saving
            ingredient_formset.instance = self.object
            step_formset.instance = self.object
            ingredient_formset.save()
            step_formset.save()
            # Get and convert category/tag IDs to integers
            category_ids = [int(cat_id) for cat_id in self.request.POST.getlist('categories')]
            tag_ids = [int(tag_id) for tag_id in self.request.POST.getlist('tags')]
   
            self.object.categories.set(category_ids)
            self.object.tags.set(tag_ids)

            return True  # Signal success
        return False  # Signal failure
    

class BaseSubRecipeView():
        model = SubRecipe
        form_class = SubRecipeForm