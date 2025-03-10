from django.forms import inlineformset_factory
from .models import Recipe, RecipeIngredient,SubRecipeIngredient,SubRecipeStep,RecipeStep, RecipeSubRecipe, SubRecipe
from .forms import RecipeIngredientForm, RecipeStepForm, RecipeForm, SubRecipeForm, SubRecipeIngredientForm, SubRecipeStepForm

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_url'] = 'title_search' 
        return context

class RecipeListView(BaseRecipeView, ListView):
    template_name = 'recipes/home.html'
    context_object_name = 'recipes'

    
    def get(self, request, *args, **kwargs):
        if request.htmx:
            return self.get_recipes(request)
        return super().get(request, *args, **kwargs)
        

    def get_recipes(self, request):
        search = request.GET.get('search_text')
        recipes = self.model.objects.filter(title__icontains=search)  if search else self.model.objects.all()
        return render(request, 'recipes/partials/recipe_list.html', {'recipes': recipes})
    

class RecipeDetailView(BaseRecipeView, DetailView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['steps'] = self.object.steps.order_by('order')
        context['ingredients'] = self.object.ingredients.all()
        
        return context
    
class RecipeCreateView(BaseRecipeView, CreateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ingredient_form_set = inlineformset_factory(Recipe, RecipeIngredient, form=RecipeIngredientForm, extra=1, can_delete=False)
        step_form_set = inlineformset_factory(Recipe, RecipeStep, form=RecipeStepForm, extra=1, can_delete=False)
        if self.request.POST:
            context['ingredient_formset'] = ingredient_form_set(self.request.POST, instance=self.object, prefix='ingredients')
            context['step_formset'] = step_form_set(self.request.POST, instance=self.object, prefix='steps')
        else:
            context['ingredient_formset'] = ingredient_form_set(instance=self.object, prefix='ingredients')
            context['step_formset'] = step_form_set(instance=self.object, prefix='steps')
        return context


    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save()

        # Ingredient formset handling
        context = self.get_context_data()
        ingredient_formset = context['ingredient_formset']
        if ingredient_formset.is_valid():
            ingredient_formset.save()
        else:
            return self.form_invalid(form)

        # Step formset handling
        step_formset = context['step_formset']
        if step_formset.is_valid():
            step_formset.save()
        else:
            return self.form_invalid(form)

        return super().form_valid(form)
    
class RecipeUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipes/recipe_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Create formsets for ingredients and steps
        ingredient_formset = inlineformset_factory(
            Recipe, RecipeIngredient, form=RecipeIngredientForm, extra=0, can_delete=True
        )
        step_formset = inlineformset_factory(
            Recipe, RecipeStep, form=RecipeStepForm, extra=0, can_delete=True
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
    
class RecipeDeleteView(BaseRecipeView,  DeleteView):
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

        ingredient_form_set = inlineformset_factory(self.model, SubRecipeIngredient,form=SubRecipeIngredientForm, extra=1, can_delete=False)
        step_form_set = inlineformset_factory(self.model, SubRecipeStep, form=SubRecipeStepForm, extra=1, can_delete=False)
        if self.request.POST:
            context['ingredient_formset'] = ingredient_form_set(self.request.POST, instance=self.object, prefix='ingredients')
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
        context['steps'] = self.object.steps.order_by('order')
        context['ingredients'] = self.object.ingredients.all()
        
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


class SubRecipeDeleteView(BaseSubRecipeView,  DeleteView):
    success_url = reverse_lazy('sub_recipes')
