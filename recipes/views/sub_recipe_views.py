from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import render

from django.core.cache import cache
from django.forms import inlineformset_factory

from helpers.mixins import RegisteredUserAuthRequired

from .base_views import BaseSubRecipeView

from ..models.sub_recipe_models import SubRecipeIngredient, SubRecipeStep, SubRecipe
from ..forms.sub_recipe_forms import SubRecipeIngredientForm, SubRecipeStepForm

class SubRecipeListView(BaseSubRecipeView, ListView):
    """
    View to display all sub recipes, it also handles search functionality.
    """
    template_name = 'sub_recipes/sub_recipe_home.html'
    context_object_name = 'sub_recipes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_url'] = 'recipes:sub_recipe_search'
        return context
    
    
    def get(self, request, *args, **kwargs):
        if request.htmx:
            return self.search(request)
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        cache_key = 'sub_recipe_list_queryset'
        cached_queryset_data = cache.get(cache_key)
        if cached_queryset_data is None:
            queryset = super().get_queryset()
            cache.set(cache_key, queryset, timeout=60 * 15)
            return queryset
        return cached_queryset_data

    def search(self, request):
        search = request.GET.get('search_text')
        search_type = request.GET.get('searchType')
        if search:
            if search_type.lower() == 'title':
                sub_recipes = self.model.objects.filter(title__icontains=search)
            else:
                sub_ingredients_to_search = [ingredient.strip() for ingredient in search.split(',') if ingredient.strip()]

                query_set = self.model.objects.all()
                for ingredient in sub_ingredients_to_search:
                    query_set = query_set.filter(sub_ingredients__name__icontains=ingredient)
                sub_recipes = query_set.distinct()
        else:
            sub_recipes = self.model.objects.all()
        return render(request, 'partials/sub_recipe_list.html', {'sub_recipes': sub_recipes})


class SubRecipeCreateView(RegisteredUserAuthRequired, BaseSubRecipeView, CreateView):
    """"
    View to create sub recipes, it also handles the creation of ingredients and steps in the sub recipe.
    """
    template_name = 'sub_recipes/sub_recipe_form.html'
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
        if ingredient_formset.is_valid() and steps_formset.is_valid():
            form.save()
            ingredient_formset.save()
            steps_formset.save()
        else:
            return super().form_invalid(form)

        return super().form_valid(form)


class SubRecipeDetailView(BaseSubRecipeView, DetailView):
    """"
    View for sub recipe details, also displays related main recipes.
    """
    template_name = 'sub_recipes/subrecipe_detail.html'

    def get_object(self, queryset=None):
        cache_key = f'sub_recipe_detail_{self.kwargs.get("pk")}'
        cached_object_data = cache.get(cache_key)
        if cached_object_data is None:
            queryset = self.get_queryset().prefetch_related('sub_ingredients', 'sub_steps', 'main_recipes')
            response = super().get_object(queryset)
            cache.set(cache_key, response, timeout=60 * 60)
            return response
        return cached_object_data
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_edit'] = self.can_edit_recipe()
        return context
    
    def can_edit_recipe(self):
        """
        Determines if the user can edit the recipe.
        """
        return self.request.user.id == self.object.author.id or self.request.user.is_staff or self.request.user.is_superuser


class SubRecipeUpdateView(RegisteredUserAuthRequired, BaseSubRecipeView, UpdateView):
    """
    View to update sub recipes.
    """
    template_name = 'sub_recipes/recipe_form.html'

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


class SubRecipeDeleteView(RegisteredUserAuthRequired, DeleteView):
    """
    View to delete sub recipes, it doesn't inherite from the becase because form_class messes up with it's logic
    """
    template_name = 'sub_recipes/subrecipe_confirm_delete.html'
    model = SubRecipe
    success_url = reverse_lazy('sub_recipes')