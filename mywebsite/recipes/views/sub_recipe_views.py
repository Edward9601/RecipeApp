from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import render

from django.forms import inlineformset_factory
from .base_views import BaseSubRecipeView

from ..models.sub_recipe_models import SubRecipeIngredient, SubRecipeStep, SubRecipe
from ..forms.sub_recipe_forms import SubRecipeIngredientForm, SubRecipeStepForm

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