import { RecipeManager } from './recipes.js';
import { SubRecipeManager } from './sub_recipes.js';
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('recipe-form')) {
        new RecipeManager();
    }
    if (document.getElementById('sub-recipe-form')) {
        new SubRecipeManager();
    }
});
//# sourceMappingURL=main.js.map