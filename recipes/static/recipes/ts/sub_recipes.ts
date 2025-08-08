import { IngredientsAndStepsManager } from './ingredients_and_steps.js';

export class SubRecipeManager {

    private mainForm: HTMLFormElement | null = null;
    
    constructor() {
        this.mainForm = document.getElementById('sub-recipe-form') as HTMLFormElement;
        if(this.mainForm){
            new IngredientsAndStepsManager();
        }
        
    }
}
