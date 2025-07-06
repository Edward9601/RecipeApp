from ..models.recipe_models import Recipe, RecipeSubRecipe
from ..models.sub_recipe_models import SubRecipe
from ..forms.recipe_forms import RecipeHomeForm
from ..forms.sub_recipe_forms import SubRecipeForm



class BaseRecipeView():
    """
    Base view for recipes to extend
    """
    model = Recipe
    form_class = RecipeHomeForm
    intermediate_table = RecipeSubRecipe        
    

class BaseSubRecipeView():
        model = SubRecipe
        form_class = SubRecipeForm