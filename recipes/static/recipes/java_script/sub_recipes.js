import { IngredientsAndStepsManager } from './ingredients_and_steps.js';
export class SubRecipeManager {
    constructor() {
        this.mainForm = null;
        this.mainForm = document.getElementById('sub-recipe-form');
        if (this.mainForm) {
            new IngredientsAndStepsManager();
        }
    }
}
//# sourceMappingURL=sub_recipes.js.map