from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.http import JsonResponse

from ..models.recipe_models import RecipeSubRecipe, Recipe, Category, Tag
from ..forms.recipe_forms import RecipeCreateForm, RecipeImageForm, RecipeHomeForm
from ..forms.recipe_filter_forms import RecipeFilterForm
from utils.helpers.mixins import RegisteredUserAuthRequired

from ..handlers import recipes_handler

class RecipeListView(ListView):
    """
    View to display all recipes
    """
    model = Recipe
    form_class = RecipeHomeForm
    template_name = 'recipes/home.html'
    context_object_name = 'recipes'
    paginate_by = 12

    def get(self, request, *args, **kwargs):
        if request.htmx:
            return self.search(request)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_url'] = 'recipes:recipe_search'
        context['filter_form'] = self.get_filter_form()
        return context

    def get_filter_form(self):
        return RecipeFilterForm(self.request.GET or None)

    def get_queryset(self):
        # Try to get cached data
        cache_key = 'recipe_list_queryset'
        queryset = recipes_handler.get_cached_object(cache_key)
        if queryset is None:
            # If not in cache, get fresh data and cache it
            queryset = super().get_queryset()
            success, error_maessage = recipes_handler.set_cached_object(cache_key, queryset, timeout=60 * 60)  # Cache for 1 hour
            if not success:
                raise Exception(f"Failed to set cache: {error_maessage}")
        form = self.get_filter_form()
        if form.is_valid():
            category = form.cleaned_data.get('category')
            tag = form.cleaned_data.get('tag')
            if category and category.exists():
                queryset = queryset.filter(categories__in=category).distinct()
            if tag and tag.exists():
                queryset = queryset.filter(tags__in=tag).distinct()
        return queryset
        

    def search(self, request):
        search_elements = request.GET.get('search_text')
        search_type = request.GET.get('searchType')

        if search_elements:
            if search_type.lower() == 'title':
                recipes = self.model.objects.filter(title__icontains=search_elements)
            elif search_type.lower() == 'ingredient':
                ingredients_to_search = [ingredient.strip() for ingredient in search_elements.split(',') if ingredient.strip()]

                query_set = self.model.objects.all()
                for ingredient in ingredients_to_search:
                    query_set = query_set.filter(ingredients__name__icontains=ingredient)
                recipes = query_set.distinct()
            else:
                return JsonResponse({'error': 'Invalid search type'}, status=400)
        else:
            recipes = self.model.objects.all()

        return render(request, 'partials/recipe_list.html', {'recipes': recipes})


class RecipeDetailView(DetailView):
    """
    View for recipe details, also displays related recipes
    """
    model = Recipe
    form_class = RecipeHomeForm

    def get_object(self, queryset=None):
        # Try to get cached data
        cache_key = f'recipe_detail_{self.kwargs.get("pk")}'
        response = recipes_handler.get_cached_object(cache_key)
        
        if response is None:
            # If not in cache, get fresh data and cache it
            queryset = self.get_queryset().prefetch_related('steps', 'ingredients', 'sub_recipes', 'categories', 'tags')
            response = super().get_object(queryset)
            success, error_message = recipes_handler.set_cached_object(cache_key, response, timeout=60 * 60)  # Cache for 1 hour
            if not success:
                raise Exception(f"Failed to set cache: {error_message}")
            return response
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_edit'] = self.can_edit_recipe()
        return context
    

    def can_edit_recipe(self):
        """
        Determines if the user can edit the recipe.
        """
        return self.request.user.id == self.object.author.id or self.request.user.is_staff or self.request.user.is_superuser



class RecipeCreateView(RegisteredUserAuthRequired, CreateView):
    """
    View to create recipes.
    """
    model = Recipe
    form_class = RecipeCreateForm
    image_form = RecipeImageForm
    intermidiate_table = RecipeSubRecipe

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        recipe_context_get = recipes_handler.fetch_recipe_context_data_for_get_request(self.object, self.image_form, extra_forms=1)
        context.update(recipe_context_get)
        return context

    def form_valid(self, form):
        """
        Handles the form submission for creating a new recipe.
        This method processes the form data, validates the ingredient and step formsets,
        and saves the recipe along with its associated ingredients, steps, categories, and tags.
        """
        form.instance.author = self.request.user
        self.object = form.save(commit=False)
        context = recipes_handler.fetch_recipe_context_data_for_post_request(self.object, self.request, self.image_form)
        success = recipes_handler.save_recipe_and_forms(self.object, context)
        if not success:
            return self.form_invalid(form)
                
        recipes_handler.save_categories_and_tags(self.object,
                                                 self.request.POST.getlist('categories'),
                                                 self.request.POST.getlist('tags'))
        # Handle sub-recipes
        sub_recipes = form.cleaned_data.get('sub_recipes')
        if sub_recipes:
            recipes_handler.save_recipe_sub_recipe_relationship(self.object, sub_recipes, 
                                                                self.intermidiate_table)
        # Clear the cache for recipe list to ensure new recipe appears
        recipes_handler.invalidate_recipe_cache()
        return redirect(self.object.get_absolute_url())
        
    

class RecipeUpdateView(RegisteredUserAuthRequired, UpdateView):
    """
    View to update recipes.
    """
    model = Recipe
    form_class = RecipeCreateForm
    image_form = RecipeImageForm
    template_name = 'recipes/recipe_form.html'
    intermidiate_table = RecipeSubRecipe

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        
        image_instance = self.model.objects.filter(id=self.object.id).first().images.first() if self.object.images.exists() else None
        recipe_context_get = recipes_handler.fetch_recipe_context_data_for_get_request(self.object, self.image_form,image_instance)
        context.update(recipe_context_get)
        return context


    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save(commit=False)
        image_instance = self.model.objects.filter(id=self.object.id).first().images.first() if self.object.images.exists() else None
        context = recipes_handler.fetch_recipe_context_data_for_post_request(self.object, self.request, self.image_form, image_instance)
        success = recipes_handler.save_recipe_and_forms(self.object, context)
        if not success:
            return self.form_invalid(form)

        recipes_handler.save_categories_and_tags(self.object,
                                                 self.request.POST.getlist('categories'),
                                                 self.request.POST.getlist('tags'))
        
        new_recipes_to_add = set(form.cleaned_data.get('sub_recipes', []))
        current_sub_recipes = set(self.object.sub_recipes.all())
        if new_recipes_to_add and new_recipes_to_add != current_sub_recipes:
            success, error_message = recipes_handler.update_recipe_sub_recipe_relationship(
                self.object, new_recipes_to_add, current_sub_recipes, self.intermidiate_table)
            if not success:
                form.add_error(None, error_message)
                return self.form_invalid(form) 
        record_id = f'recipe_detail_{self.object.id}'
        recipes_handler.invalidate_recipe_cache(record_id)
        
        return redirect(self.get_success_url())
    



class RecipeDeleteView(DeleteView):
    """
    View to delete recipes.
    """
    model = Recipe
    success_url = reverse_lazy('recipes:home')

    def delete(self, request, *args, **kwargs):
        """ 
        Handles the deletion of a recipe.
        This method overrides the default delete method to ensure that the recipe is deleted
        and the cache is invalidated for both the recipe detail and the recipe list.
        """
        # Invalidate cache for this recipe and the recipe list
        cache_key_detail = f'recipe_detail_{self.kwargs.get("pk")}'
        recipes_handler.invalidate_recipe_cache(cache_key_detail)

        return super().delete(request, *args, **kwargs)
    

    def post(self, request, *args, **kwargs):
        """
        Handles the POST request for deleting a recipe.
        This method overrides the default post method to ensure that the recipe is deleted
        and the cache is invalidated for both the recipe detail and the recipe list.
        """
        return self.delete(request, *args, **kwargs)



def get_categories_and_tags(request):
    """
    Returns categories and tags as JSON response.
    """
    
    categories = Category.objects.all()
    tags = Tag.objects.all()

    data = {
        'categories': [{'id': category.id, 'name': category.name} for category in categories],
        'tags': [{'id': tag.id, 'name': tag.name} for tag in tags]
    }
    return JsonResponse(data)