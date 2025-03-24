from django.forms import inlineformset_factory
from django import forms
from .models.recipe_models import Recipe, RecipeIngredient, RecipeStep, RecipeSubRecipe
from .models.sub_recipe_models import SubRecipeIngredient, SubRecipeStep, SubRecipe
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
    form = RecipeForm
    intermediate_table = RecipeSubRecipe


class RecipeListView(BaseRecipeView, ListView):
    """
    View to display all recipes
    """

    template_name = 'recipes/home.html'
    context_object_name = 'recipes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_url'] = 'recipe_search'
        return context

    def get(self, request, *args, **kwargs):
        if request.htmx:
            return self.search(request)
        return super().get(request, *args, **kwargs)

    def search(self, request):
        search = request.GET.get('search_text')
        search_type = request.GET.get('searchType')
        if search:
            if search_type.lower() == 'title':
                recipes = self.model.objects.filter(title__icontains=search)
            if search_type.lower() == 'ingredients':
                recipes = self.model.objects.filter(ingredients__name__icontains=search).distinct()
            else:
                pass # TODO add 400 response
        else:
            recipes = self.model.objects.all()
        return render(request, 'recipes/partials/recipe_list.html', {'recipes': recipes})


class RecipeDetailView(BaseRecipeView, DetailView):
    """
    View for recipe details, also displays related recipes
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object = self.model.objects.prefetch_related('steps','ingredients', 'sub_recipes').get(pk=self.object.pk)
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
            return super().form_invalid(form)

        return super().form_valid(form)


class RecipeCreateView(BaseViewForDataUpdate, CreateView):
    """
    View to create recipes.
    """

    def form_valid(self, form):
        response = super().form_valid(form)
        sub_recipes = form.cleaned_data.get('sub_recipes')
        if sub_recipes:
            for sub_recipe in sub_recipes:
                RecipeSubRecipe.objects.create(recipe=self.object,
                                               sub_recipe=sub_recipe)
        return response


class RecipeUpdateView(BaseViewForDataUpdate, UpdateView):
    """
    View to update recipes.
    """

    template_name = 'recipes/recipe_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        if self.object.sub_recipes.all():
            form.fields['sub_recipes'].initial = self.object.sub_recipes.all() # ensures that previosly selected sub recipes appear as checked.
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        new_recipes_to_add = set(form.cleaned_data.get('sub_recipes', []))
        current_sub_recipes = set(self.object.sub_recipes.all())

        sub_recipes_to_add = new_recipes_to_add - current_sub_recipes
        to_remove = current_sub_recipes - new_recipes_to_add

        if to_remove:
            self.intermediate_table.objects.filter(recipe=self.object, sub_recipe__in=to_remove).delete()
        if sub_recipes_to_add:
            RecipeSubRecipe.objects.bulk_create([RecipeSubRecipe(recipe=self.object,
                                               sub_recipe=sub_recipe) for sub_recipe in sub_recipes_to_add])
        return response

class RecipeDeleteView(LoginRequiredMixin, DeleteView):
    """
    View to delete recipes.
    """
    model = Recipe
    success_url = reverse_lazy('home')


class BaseSubRecipeView(LoginRequiredMixin):
    model = SubRecipe
    form_class = SubRecipeForm


class SubRecipeListView(BaseSubRecipeView, ListView):
    template_name = 'recipes/sub_recipe.html'
    context_object_name = 'sub_recipes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_url'] = 'sub_recipe_search'
        return context

    def get(self, request, *args, **kwargs):
        if request.htmx:
            return self.search(request)
        else:
            return super().get(request, *args, **kwargs)

    def search(self, request):
        search = request.GET.get('search_text')
        search_type = request.GET.get('searchType')
        if search:
            if search_type.lower() == 'title':
                sub_recipes = self.model.objects.filter(title__icontains=search)
            else:
                sub_recipes = self.model.objects.filter(sub_ingredients__name__icontains=search).distinct()
        else:
            sub_recipes = self.model.objects.all()
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
        self.object = form.save(commit=False)

        context = self.get_context_data()
        ingredient_formset = context['ingredient_formset']
        steps_formset = context['step_formset']
        if ingredient_formset.is_valid() or steps_formset.is_valid():
            form.save()
            ingredient_formset.save()
            steps_formset.save()
        else:
            return super().form_invalid(form)

        return super().form_valid(form)


class SubRecipeDetailView(BaseSubRecipeView, DetailView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object = self.model.objects.prefetch_related('sub_ingredients', 'sub_steps', 'main_recipes')
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
        self.object = form.save(commit=False)

        context = self.get_context_data()
        ingredient_formset = context['ingredient_formset']
        steps_formset = context['step_formset']

        if ingredient_formset.is_valid() or steps_formset.is_valid():
            ingredient_formset.save()
            steps_formset.save()
            form.save()
        else:
            return self.form_invalid(form)
        return super().form_valid(form)


class SubRecipeDeleteView(LoginRequiredMixin, DeleteView):
    """
    View to delete sub recipes, it doesn't inherite from the becase because form_class messes up with it's logic
    """
    model = SubRecipe
    success_url = reverse_lazy('sub_recipes')
    
