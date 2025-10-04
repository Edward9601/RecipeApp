from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db import transaction, IntegrityError

from ..models.recipe_models import RecipeSubRecipe, Recipe, Category, Tag
from ..forms.recipe_forms import RecipeCreateForm, RecipeImageForm, RecipeHomeForm, RecipeIngredientForm, RecipeStepForm
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

        return render(request, 'recipes/partials/recipe_list.html', {'recipes': recipes})


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
    template_name = 'recipes/recipe_create.html'

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
    template_name = 'recipes/recipe_update.html'
    intermidiate_table = RecipeSubRecipe

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        
        image_instance = self.model.objects.filter(id=self.object.id).first().images.first() if self.object.images.exists() else None
        recipe_context_get = recipes_handler.fetch_recipe_context_data_for_update(self.object, self.image_form,image_instance)
        context.update(recipe_context_get)
        return context


    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save(commit=False)
        image_form = None
        if self.request.FILES:
            image_instance = self.model.objects.filter(
                id=self.object.id).first().images.first() if self.object.images.exists() else None
            # If there are files in the request, ensure the image form is included
            image_form = self.image_form(self.request.POST,
                                            self.request.FILES,
                                            instance=image_instance)
            if not image_form.is_valid(): 
                return self.form_invalid(form)   
        
        try:
            with transaction.atomic():
                self.object.save()                      
                recipes_handler.save_categories_and_tags(self.object,
                                                        self.request.POST.getlist('categories'),
                                                        self.request.POST.getlist('tags'))
                
                new_recipes_to_add = set(form.cleaned_data.get('sub_recipes', []))
                current_sub_recipes = set(self.object.sub_recipes.all())
                if new_recipes_to_add and new_recipes_to_add != current_sub_recipes:
                    success, error_message = recipes_handler.update_recipe_sub_recipe_relationship(
                        self.object, new_recipes_to_add, current_sub_recipes, self.intermidiate_table)
                    if not success:     
                        raise ValueError(error_message)

                if image_form:
                    image_instance = image_form.save(commit=False)
                    if getattr(image_instance, 'recipe', None) is None:
                        image_instance.recipe = self.object
                        image_instance.save()
                record_id = f'recipe_detail_{self.object.id}'
                transaction.on_commit(lambda: recipes_handler.invalidate_recipe_cache(record_id))

        except ValueError as ve:
            # attach the error to the form and return invalid
            form.add_error(None, str(ve))
            return self.form_invalid(form)
        except IntegrityError as ie:
            form.add_error(None, "Database error occurred")
            return self.form_invalid(form)
        except Exception:
            # log as needed
            form.add_error(None, "Failed to save recipe")
            return self.form_invalid(form) 
        
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


class IngredientsPartialView(RegisteredUserAuthRequired, View):
    """
    Handles ingredient modal requests for both new and existing recipes.
    Supports both GET (display form) and POST (save ingredients).
    """

    model = Recipe
    form_class = RecipeIngredientForm
    template_name = 'recipes/html_modals/ingredients_modal.html'

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        context = self._get_ingredients_context(pk)
        
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk:
            return self._handle_update_post_request(request, pk)
        error_response = {
            'errorMessage': 'Request missing recipe ID.'
        }
        return JsonResponse(error_response, status=400)


    def _get_ingredients_context(self, pk=None):
        if pk:
            cache_key = f'recipe_ingredients_{pk}'
            context = recipes_handler.get_cached_object(cache_key)
            if not context:
                recipe = self.model.objects.get(id=pk)
                context = recipes_handler.fetch_partial_recipe_context_data_for_get(recipe, 'ingredients')
                recipes_handler.set_cached_object(cache_key, context)
        else:
            cache_key = f'recipe_ingredients'
            context = recipes_handler.get_cached_object(cache_key)
            if not context:
                context = recipes_handler.fetch_partial_recipe_context_data_for_get(None,'ingredients', extra_forms=1)
                recipes_handler.set_cached_object(cache_key, context)
        return context
 

    def _handle_update_post_request(self, request, pk):
        """
        Handles the POST request for updating ingredients of an existing recipe.
        This method processes the form data, validates the ingredient formset,
        and updates the recipe's ingredients.
        """
        
        try:
            recipe = get_object_or_404(self.model, pk=pk)
            context = recipes_handler.fetch_partial_form_for_post_request(request, 'ingredients', recipe)

            ingredients_formset = context.get('ingredients_formset')
            if ingredients_formset.is_valid():
                ingredients_formset.save()
                ingredients_cache_key = f'recipe_ingredients_{pk}'
                recipe_ingredients_cache_key = f'recipe_detail_{pk}'
                recipes_handler.invalidate_recipe_cache(recipe_ingredients_cache_key)
                recipes_handler.invalidate_recipe_cache(ingredients_cache_key)

                updated_ingredients = [
                    {
                        'id': ing.id,
                        'name': ing.name,
                        'quantity': ing.quantity or '',
                        'measurement': ing.measurement or ''
                    }
                    for ing in recipe.ingredients.all()
                ]
                message = {'success': True,
                           'ingredients': updated_ingredients, 
                           'errorMessage': '',
                           'status': 204}
                return JsonResponse(message)
            error_response = {'success': False,
                              'errorMessage': 'There were errors in the form submission.',
                              'formErrors': ingredients_formset.management_form.errors,
                              'status': 400
            }
            return JsonResponse(error_response)
        except self.model.DoesNotExist:
            error_response = {'success': False,
                            'errorMessage': 'Recipe not found.',
                            'status' : 404
            }
            return JsonResponse(error_response)
        


class StepsPartialView(RegisteredUserAuthRequired, View):
    """
    Handles steps modal requests for both new and existing recipes.
    Supports both GET (display form) and POST (save steps).
    """

    model = Recipe
    form_class = RecipeStepForm
    template_name = 'recipes/html_modals/steps_modal.html'

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        context = self._get_steps_context(pk)
        
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk:
            return self._handle_update_post_request(request, pk)
        error_response = {
            'errorMessage': 'Request missing recipe ID.'
        }
        return JsonResponse(error_response, status=400)


    def _get_steps_context(self, pk=None):
        if pk:
            cache_key = f'recipe_steps_{pk}'
            context = recipes_handler.get_cached_object(cache_key)
            if not context:
                recipe = self.model.objects.get(id=pk)
                context = recipes_handler.fetch_partial_recipe_context_data_for_get(recipe, 'steps')
                recipes_handler.set_cached_object(cache_key, context)
        else:
            cache_key = f'recipe_steps'
            context = recipes_handler.get_cached_object(cache_key)
            if not context:
                context = recipes_handler.fetch_partial_recipe_context_data_for_get(None, 'steps', extra_forms=1)
                recipes_handler.set_cached_object(cache_key, context)
        return context


    def _handle_update_post_request(self, request, pk):
        """
        Handles the POST request for updating steps of an existing recipe.
        This method processes the form data, validates the ingredient formset,
        and updates the recipe's steps.
        """
        
        try:
            recipe = get_object_or_404(self.model, pk=pk)
            context = recipes_handler.fetch_partial_form_for_post_request(request,'steps', recipe)

            steps_formset = context.get('steps_formset')
            if steps_formset.is_valid():
                steps_formset.save()
                ingredients_cache_key = f'recipe_steps_{pk}'
                recipe_ingredients_cache_key = f'recipe_detail_{pk}'
                recipes_handler.invalidate_recipe_cache(recipe_ingredients_cache_key)
                recipes_handler.invalidate_recipe_cache(ingredients_cache_key)

                updated_steps = [
                    {
                        'id': step.id,
                        'order': step.order,
                        'description': step.description or ''
                    }
                    for step in recipe.steps.all()
                ]
                message = {'success': True,
                           'steps': updated_steps, 
                           'errorMessage': '',
                           'status': 204}
                return JsonResponse(message)
            error_response = {'success': False,
                              'errorMessage': 'There were errors in the form submission.',
                              'formErrors': steps_formset.management_form.errors,
                              'status': 400
            }
            return JsonResponse(error_response)
        except self.model.DoesNotExist:
            error_response = {'success': False,
                            'errorMessage': 'Recipe not found.',
                            'status' : 404
            }
            return JsonResponse(error_response)
        

