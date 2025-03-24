from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import render

from .base_views import BaseRecipeView, BaseViewForDataUpdate
from ..models.recipe_models import RecipeSubRecipe, Recipe

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