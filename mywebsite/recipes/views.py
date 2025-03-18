from django.forms import inlineformset_factory
from django import forms
from .models import Recipe, RecipeIngredient, SubRecipeIngredient, SubRecipeStep, RecipeStep, RecipeSubRecipe, SubRecipe
from .forms import RecipeIngredientForm, RecipeStepForm, RecipeForm, SubRecipeForm, SubRecipeIngredientForm, \
    SubRecipeStepForm

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import render


class BaseRecipeView(LoginRequiredMixin):
    """
    Base view for recipes to extend
    """
    model = Recipe
    form_class = RecipeForm
    intermediate_table = RecipeSubRecipe


class RecipeListView(BaseRecipeView, ListView):
    """
    View to display all recipes
    """
     
    template_name = 'recipes/home.html'
    context_object_name = 'recipes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_url'] = 'title_search'
        return context

    def get(self, request, *args, **kwargs):
        if request.htmx:
            return self.get_recipes(request)
        return super().get(request, *args, **kwargs)

    def get_recipes(self, request):
        search = request.GET.get('search_text')
        recipes = self.model.objects.filter(title__icontains=search) if search else self.model.objects.all()
        return render(request, 'recipes/partials/recipe_list.html', {'recipes': recipes})


class RecipeDetailView(BaseRecipeView, DetailView):
    """
    View for recipe details, also displays related recipes
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['steps'] = self.object.steps.order_by('order')
        context['ingredients'] = self.object.ingredients.all()
        context['sub_recipes'] = self.object.sub_recipes.all()
        sub_recipes = self.object.sub_recipes.all()
        if sub_recipes:
            for sub_recipe in sub_recipes:
                print(sub_recipe.ingredients.all())
        return context
    

class BaseViewForDataUpdate(BaseRecipeView):
    """
    Base view to handle create and update operation on recipes.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_formset_count = 0
        if isinstance(self, RecipeCreateView):
            extra_formset_count = 1
        ingredient_form_set = inlineformset_factory(Recipe, RecipeIngredient, form=RecipeIngredientForm, extra=extra_formset_count,
                                                    can_delete=True)
        step_form_set = inlineformset_factory(Recipe, RecipeStep, form=RecipeStepForm, extra=extra_formset_count, can_delete=True)
        if self.request.POST:
            context['ingredient_formset'] = ingredient_form_set(self.request.POST, instance=self.object, prefix='ingredients')
            context['step_formset'] = step_form_set(self.request.POST, instance=self.object, prefix='steps')
        else:
            context['ingredient_formset'] = ingredient_form_set(instance=self.object, prefix='ingredients')
            context['step_formset'] = step_form_set(instance=self.object, prefix='steps')
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
            print("Ingredient Formset Errors:", ingredient_formset.errors)
            print("Step Formset Errors:", step_formset.errors)
            return self.form_invalid(form)
        
        return super().form_valid(form)

class RecipeCreateView(BaseViewForDataUpdate, CreateView):
    """
    View to create recipes.
    """

    def form_valid(self, form):
        response = super().form_valid(form)
        sub_recipes = form.cleaned_data.get('sub_recipes')
        if sub_recipes:
            for sub_recipe in  sub_recipes:
                RecipeSubRecipe.objects.create(recipe=self.object,
                                               sub_recipe=sub_recipe)
        return response

class RecipeUpdateView(BaseViewForDataUpdate, UpdateView):
    """
    View to update recipes.
    """
    
    template_name = 'recipes/recipe_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        sub_recipes = form.cleaned_data.get('sub_recipes')
        if sub_recipes:
            self.intermediate_table.objects.filter(recipe=self.object).delete()
            for sub_recipe in  sub_recipes:
                RecipeSubRecipe.objects.create(recipe=self.object,
                                               sub_recipe=sub_recipe)
        return response
        


class RecipeDeleteView(BaseRecipeView, DeleteView):
    """
    View to delete recipes.
    """

    success_url = reverse_lazy('home')


class BaseSubRecipeView(LoginRequiredMixin):
    model = SubRecipe
    form_class = SubRecipeForm


class SubRecipeListView(BaseSubRecipeView, ListView):
    template_name = 'recipes/sub_recipe.html'
    context_object_name = 'sub_recipes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_url'] = 'sub_recipe_title_search'
        return context

    def get(self, request, *args, **kwargs):
        if request.htmx:
            return self.search_subrecipes(request)
        else:
            return super().get(request, *args, **kwargs)

    def search_subrecipes(self, request):
        search = request.GET.get('search_text')
        sub_recipes = self.model.objects.filter(title__icontains=search) if search else self.model.objects.all()
        return render(request, 'recipes/partials/sub_recipe_list.html', {'sub_recipes': sub_recipes})


class SubRecipeCreateView(BaseSubRecipeView, CreateView):
    template_name = 'recipes/sub_recipe_form.html'
    success_url = reverse_lazy('sub_recipes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ingredient_form_set = inlineformset_factory(self.model, SubRecipeIngredient, form=SubRecipeIngredientForm,
                                                    extra=1, can_delete=False)
        step_form_set = inlineformset_factory(self.model, SubRecipeStep, form=SubRecipeStepForm, extra=1,
                                              can_delete=False)
        if self.request.POST:
            context['ingredient_formset'] = ingredient_form_set(self.request.POST, instance=self.object,
                                                                prefix='ingredients')
            context['step_formset'] = step_form_set(self.request.POST, instance=self.object, prefix='steps')
        else:
            context['ingredient_formset'] = ingredient_form_set(instance=self.object, prefix='ingredients')
            context['step_formset'] = step_form_set(instance=self.object, prefix='steps')
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save()

        context = self.get_context_data()
        ingredient_formset = context['ingredient_formset']
        if ingredient_formset.is_valid():
            ingredient_formset.save()
        else:
            return self.form_invalid(form)
        steps_formset = context['step_formset']
        if steps_formset.is_valid():
            steps_formset.save()
        else:
            return self.form_invalid(form)

        return super().form_valid(form)


class SubRecipeDetailView(BaseSubRecipeView, DetailView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['steps'] = self.object.sub_steps.order_by('order')
        context['ingredients'] = self.object.sub_ingredients.all()

        return context


class SubRecipeUpdateView(BaseSubRecipeView, UpdateView):
    template_name = 'recipes/recipe_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Create formsets for ingredients and steps in sub recipe
        ingredient_formset = inlineformset_factory(
            SubRecipe, SubRecipeIngredient, form=SubRecipeIngredientForm, extra=0, can_delete=True
        )
        step_formset = inlineformset_factory(
            SubRecipe, SubRecipeStep, form=SubRecipeStepForm, extra=0, can_delete=True
        )

        if self.request.POST:
            context['ingredient_formset'] = ingredient_formset(self.request.POST, instance=self.object)
            context['step_formset'] = step_formset(self.request.POST, instance=self.object)
        else:
            context['ingredient_formset'] = ingredient_formset(instance=self.object)
            context['step_formset'] = step_formset(instance=self.object)

        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save()

        context = self.get_context_data()
        ingredient_formset = context['ingredient_formset']
        if ingredient_formset.is_valid():
            ingredient_formset.save()
        else:
            return self.form_invalid(form)
        steps_formset = context['step_formset']
        if steps_formset.is_valid():
            steps_formset.save()
        else:
            return self.form_invalid(form)

        return super().form_valid(form)


class SubRecipeDeleteView(BaseSubRecipeView, DeleteView):
    success_url = reverse_lazy('sub_recipes')
