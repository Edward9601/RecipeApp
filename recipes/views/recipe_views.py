from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.cache import cache

from .base_views import BaseRecipeView
from ..models.recipe_models import RecipeSubRecipe, Recipe, Category, Tag
from ..forms.recipe_forms import RecipeCreateForm, RecipeImageForm
from ..forms.recipe_filter_forms import RecipeFilterForm
from utils.helpers.mixins import RegisteredUserAuthRequired

from ..handlers import recipes_handler

class RecipeListView(BaseRecipeView, ListView):
    """
    View to display all recipes
    """

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
        queryset = cache.get(cache_key)
        if queryset is None:
            # If not in cache, get fresh data and cache it
            queryset = super().get_queryset()
            cache.set(cache_key, queryset, timeout=60 * 15)  # Cache for 15 minutes
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
        search = request.GET.get('search_text')
        search_type = request.GET.get('searchType')

        if search:
            if search_type.lower() == 'title':
                recipes = self.model.objects.filter(title__icontains=search)
            elif search_type.lower() == 'ingredient':
                ingredients_to_search = [ingredient.strip() for ingredient in search.split(',') if ingredient.strip()]

                query_set = self.model.objects.all()
                for ingredient in ingredients_to_search:
                    query_set = query_set.filter(ingredients__name__icontains=ingredient)
                recipes = query_set.distinct()
            else:
                return JsonResponse({'error': 'Invalid search type'}, status=400)
        else:
            recipes = self.model.objects.all()

        return render(request, 'partials/recipe_list.html', {'recipes': recipes})


class RecipeDetailView(BaseRecipeView, DetailView):
    """
    View for recipe details, also displays related recipes
    """

    def get_object(self, queryset=None):
        # Try to get cached data
        cache_key = f'recipe_detail_{self.kwargs.get("pk")}'
        cached_object_data = cache.get(cache_key)
        
        if cached_object_data is None:
            # If not in cache, get fresh data and cache it
            queryset = self.get_queryset().prefetch_related('steps', 'ingredients', 'sub_recipes', 'categories', 'tags')
            response = super().get_object(queryset)
            cache.set(cache_key, response, timeout=60 * 60)  # Cache for 1 hour
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



class RecipeCreateView(RegisteredUserAuthRequired, CreateView):
    """
    View to create recipes.
    """
    model = Recipe
    form_class = RecipeCreateForm
    image_form = RecipeImageForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context.update(recipes_handler.populate_context_data_for_post(self))
        else:
            context.update(recipes_handler.populate_context_data_for_get(self))
        return context

    def form_valid(self, form):
        """
        Handles the form submission for creating a new recipe.
        This method processes the form data, validates the ingredient and step formsets,
        and saves the recipe along with its associated ingredients, steps, categories, and tags.
        """
        form.instance.author = self.request.user
        self.object = form.save(commit=False)
        context = self.get_context_data()

        ingredient_formset = context['ingredient_formset']
        step_formset = context['step_formset']
        image_form = context.get('image_from', None)

        forms_list = [ingredient_formset, step_formset]
        if recipes_handler.are_forms_valid(forms_list):
            self.object.save()
            if image_form:
                if image_form.is_valid():
                    # Save the image form if it is valid
                    recipes_handler.save_image_form(self.object, image_form)
                else:
                    return self.form_invalid(image_form)
                
            recipes_handler.save_valid_forms(self.object, forms_list)
            category_ids = [int(cat_id) for cat_id in self.request.POST.getlist('categories')]
            tag_ids = [int(tag_id) for tag_id in self.request.POST.getlist('tags')]
   
            self.object.categories.set(category_ids)
            self.object.tags.set(tag_ids)
            # Handle sub-recipes
            sub_recipes = form.cleaned_data.get('sub_recipes')
            if sub_recipes:
                for sub_recipe in sub_recipes:
                    RecipeSubRecipe.objects.create(recipe=self.object, sub_recipe=sub_recipe)

            # Clear the cache for recipe list to ensure new recipe appears
            invalidate_recipe_cache()
            return redirect(self.object.get_absolute_url())
        return self.form_invalid(form)
    

class RecipeUpdateView(RegisteredUserAuthRequired, UpdateView):
    """
    View to update recipes.
    """
    model = Recipe
    form_class = RecipeCreateForm
    image_form = RecipeImageForm
    template_name = 'recipes/recipe_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        image_instance = self.model.objects.filter(id=self.object.id).first().images.first() if self.object.images.exists() else None
        if self.request.POST:
            context.update(recipes_handler.populate_context_data_for_post(self, image_instance))
        else:
            context.update(recipes_handler.populate_context_data_for_get(self, image_instance))
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        if self.object.sub_recipes.all():
            form.fields['sub_recipes'].initial = self.object.sub_recipes.all()  # ensures that previosly selected sub recipes appear as checked.
        elif self.object.categories.all():
            form.fields['categories'].initial = self.object.categories.all()
        elif self.object.tags.all():
            form.fields['tags'].initial = self.object.tags.all()
        return form

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save(commit=False)
        context = self.get_context_data()

        ingredient_formset = context['ingredient_formset']
        step_formset = context['step_formset']
        image_form = context.get('image_from', None)

        forms_list = [ingredient_formset, step_formset]
        if recipes_handler.are_forms_valid(forms_list):
            self.object.save()
            if image_form:
                if image_form.is_valid():
                    # Save the image form if it is valid
                    recipes_handler.save_image_form(self.object, image_form)
                else:
                    return self.form_invalid(image_form)
                
            recipes_handler.save_valid_forms(self.object, forms_list)
            category_ids = [int(cat_id) for cat_id in self.request.POST.getlist('categories')]
            tag_ids = [int(tag_id) for tag_id in self.request.POST.getlist('tags')]
   
            self.object.categories.set(category_ids)
            self.object.tags.set(tag_ids)
            new_recipes_to_add = set(form.cleaned_data.get('sub_recipes', []))
            current_sub_recipes = set(self.object.sub_recipes.all())

            sub_recipes_to_add = new_recipes_to_add - current_sub_recipes
            to_remove = current_sub_recipes - new_recipes_to_add

            if to_remove:
                self.intermediate_table.objects.filter(recipe=self.object, sub_recipe__in=to_remove).delete()
            if sub_recipes_to_add:
                RecipeSubRecipe.objects.bulk_create([RecipeSubRecipe(recipe=self.object,
                                                                    sub_recipe=sub_recipe) for sub_recipe in
                                                    sub_recipes_to_add])
            record_id = f'recipe_detail_{self.object.id}'
            invalidate_recipe_cache(record_id)
            
            return redirect(self.get_success_url())
        return self.form_invalid(form)



class RecipeDeleteView(DeleteView):
    """
    View to delete recipes.
    """
    model = Recipe
    success_url = reverse_lazy('recipes:home')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        print('test')
        # Invalidate cache for this recipe and the recipe list
        cache_key_detail = f'recipe_detail_{self.object.id}'
        invalidate_recipe_cache(cache_key_detail)

        return super().delete(request, *args, **kwargs)
    

    def post(self, request, *args, **kwargs):
        print("POST method hit")
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


def invalidate_recipe_cache(recipe_id=None):
    """
    Invalidates the recipe cache.
    """
    if recipe_id:
        cache_key_detail = f'recipe_detail_{recipe_id}'
        cache.delete(cache_key_detail)
    cache.delete('recipe_list_queryset')
    return JsonResponse({'status': 'Cache invalidated'})

