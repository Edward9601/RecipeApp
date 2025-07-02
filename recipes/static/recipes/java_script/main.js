import { RecipeManager } from './recipes.js';
import { SubRecipeManager } from './sub_recipes.js';
import { FilterPanelManager } from './filter_panel.js';
document.addEventListener('DOMContentLoaded', () => {
    new FilterPanelManager();
    if (document.getElementById('recipe-form')) {
        new RecipeManager();
    }
    if (document.getElementById('sub-recipe-form')) {
        new SubRecipeManager();
    }
});
//# sourceMappingURL=main.js.map