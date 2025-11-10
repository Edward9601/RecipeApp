from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.core.cache import cache
from django.db import transaction, IntegrityError

from utils.helpers.mixins import RegisteredUserAuthRequired
from ..models.recipe_models import RecipeSubRecipe, Recipe
from ..forms.recipe_forms import SubRecipeCreateForm, SubRecipeUpdateForm
from ..handlers import recipes_handler
from ..handlers.recipes_handler import invalidate_recipe_cache

class SubRecipeListView(ListView):
    """
    View to display all sub recipes, it also handles search functionality.
    """
    model = Recipe
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
            queryset = queryset.filter(is_sub_recipe=True).prefetch_related('ingredients', 'steps')
            cache.set(cache_key, queryset, timeout=60 * 15)
            return queryset
        return cached_queryset_data

    def search(self, request):
        search = request.GET.get('search_text')
        search_type = request.GET.get('searchType')
        if search:
            if search_type.lower() == 'title':
                sub_recipes = self.model.objects.filter(title__icontains=search, is_sub_recipe=True)
            else:
                sub_ingredients_to_search = [ingredient.strip() for ingredient in search.split(',') if ingredient.strip()]

                query_set = self.model.objects.filter(is_sub_recipe=True)
                for ingredient in sub_ingredients_to_search:
                    query_set = query_set.filter(ingredients__name__icontains=ingredient)
                sub_recipes = query_set.distinct()
        else:
            sub_recipes = self.model.objects.filter(is_sub_recipe=True)
        return render(request, 'recipes/partials/sub_recipe_list.html', {'sub_recipes': sub_recipes})


class SubRecipeCreateView(RegisteredUserAuthRequired, CreateView):
    """"
    View to create sub recipes, it also handles the creation of ingredients and steps in the sub recipe.
    """
    model = Recipe
    form_class = SubRecipeCreateForm
    intermidiate_table = RecipeSubRecipe
    template_name = 'sub_recipes/sub_recipe_form.html'
    success_url = reverse_lazy('sub_recipes')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['extra_forms'] = 1
        return kwargs

    def form_valid(self, form):
        try:
            with transaction.atomic():
                self.object = form.save()
                sub_recipes = form.cleaned_data.get('sub_recipes')
                if sub_recipes:
                    form.save_recipe_sub_recipe_relationship(self.object, sub_recipes, 
                                                                    self.intermidiate_table)
            transaction.on_commit(lambda: recipes_handler.invalidate_recipe_cache())
        except ValueError as ve:
            # attach the error to the form and return invalid
            form.add_error(None, str(ve))
            return self.form_invalid(form)
        except IntegrityError as ie:
            form.add_error(None, "Database error occurred")
            return self.form_invalid(form)
        except Exception as e:
            # log as needed
            form.add_error(None, "Failed to save recipe")
            return self.form_invalid(form) 
        
        return redirect(self.object.get_absolute_url())


class SubRecipeDetailView(DetailView):
    """"
    View for sub recipe details, also displays related main recipes.
    """
    model = Recipe
    template_name = 'sub_recipes/subrecipe_detail.html'

    def get_object(self, queryset=None):
        cache_key = f'sub_recipe_detail_{self.kwargs.get("pk")}'
        cached_object_data = cache.get(cache_key)
        if cached_object_data is None:
            queryset = self.get_queryset().prefetch_related('ingredients', 'steps', 'parent_recipe')
            response = super().get_object(queryset)
            cache.set(cache_key, response, timeout=60 * 60)
            return response
        return cached_object_data
    

    def get_context_data(self, **kwargs):
        """
        Adds additional context to the template, including whether the user can edit the recipe.
        """
        context = super().get_context_data(**kwargs)
        context['can_edit'] = self.can_edit_sub_recipe()
        return context
    
    def can_edit_sub_recipe(self):
        """
        Determines if the user can edit the recipe.
        """
        return self.request.user.id == self.object.author.id or self.request.user.is_staff or self.request.user.is_superuser


class SubRecipeUpdateView(RegisteredUserAuthRequired, UpdateView):
    """
    View to update sub recipes.
    """
    model = Recipe
    form_class = SubRecipeUpdateForm
    intermidiate_table = RecipeSubRecipe
    template_name = 'sub_recipes/sub_recipe_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['extra_forms'] = 0
        return kwargs

    def form_valid(self, form):
        try:
            with transaction.atomic():
                self.object = form.save()
                if 'sub_recipes' in form.changed_data:
                    existing_sub_recipes = set(self.object.sub_recipe.all())
                    new_sub_recipes = set(form.cleaned_data.get('sub_recipes'))
                    sub_recipe_id = f'sub_recipe_detail_{self.object.pk}'
                    if not existing_sub_recipes:
                        if new_sub_recipes:
                            form.save_recipe_sub_recipe_relationship(
                                self.object,
                                new_sub_recipes,
                                self.intermidiate_table
                            )
                    if existing_sub_recipes != new_sub_recipes:
                        # Remove old relationships
                        success, message = form.update_recipe_sub_recipe_relationship(
                            self.object,
                            new_sub_recipes,
                            existing_sub_recipes,
                            self.intermidiate_table
                        )
                        if not success:
                            raise ValueError(message)
                    # Invalidate cache for this sub recipe
            transaction.on_commit(lambda: recipes_handler.invalidate_recipe_cache(sub_recipe_id))
        except ValueError as ve:
            # attach the error to the form and return invalid
            form.add_error(None, str(ve))
            return self.form_invalid(form)
        except IntegrityError as ie:
            form.add_error(None, "Database error occurred")
            return self.form_invalid(form)
        except Exception as e:
            # log as needed
            form.add_error(None, "Failed to save recipe")
            return self.form_invalid(form) 
        
        return redirect(self.get_success_url())
        


class SubRecipeDeleteView(RegisteredUserAuthRequired, DeleteView):
    """
    View to delete sub recipes, it doesn't inherite from the becase because form_class messes up with it's logic
    """
    template_name = 'sub_recipes/subrecipe_confirm_delete.html'
    model = Recipe
    success_url = reverse_lazy('recipes:sub_recipes')

    def delete(self, request, *args, **kwargs):
        """ 
        Handles the deletion of a sub recipe.
        This method overrides the default delete method to ensure that the sin recipe is deleted
        and the cache is invalidated for both the detail and list sub recipes.
        """
        # Invalidate cache for this recipe and the recipe list
        cache_key_detail = f'sub_recipe_detail_{self.kwargs.get("pk")}'
        invalidate_recipe_cache(cache_key_detail)
        return super().delete(request, *args, **kwargs)
    

    def post(self, request, *args, **kwargs):
        """
        Handles the POST request for deleting a sub recipe.
        This method overrides the default post method to ensure that the sub recipe is deleted
        and the cache is invalidated for both the detail and list sub recipes.
        """
        return self.delete(request, *args, **kwargs)
    

def invalidate_recipe_cache(recipe_id=None):
    """
    Invalidates the sub recipe cache.
    """
    if recipe_id:
        cache_key_detail = f'sub_recipe_detail_{recipe_id}'
        cache.delete(cache_key_detail)
    cache.delete('sub_recipe_list_queryset')