import { IngredientsAndStepsManager } from './ingredients_and_steps.js';

enum elementIdentifier {
    CATEGORIES = 'categories',
    TAGS = 'tags'
}

export class RecipeManager {

    private mainForm: HTMLFormElement | null = null;

    // Cattegories and tags block
    // Using Sets to avoid duplicates and for easier management
    private selectedCategories: Set<number> = new Set();
    private selectedTags: Set<number> = new Set();
    private categoriesAndTagsModal: HTMLElement | null = null;

    // Flag to ensure initial selections are loaded only once
    private initialeSelectionsLoaded: boolean = false;

    private subRecipesModal: HTMLElement | null = null;
    private subRecipesButton: HTMLButtonElement | null = null;
    private selectedSubRecipes: Set<number> = new Set();
    private initialSubRecipeSelectionLoaded: boolean = false;

    


    private imagePreview: HTMLImageElement | null = null;

    
    constructor() {
        this.mainForm = document.getElementById('recipe-form') as HTMLFormElement;
        this.categoriesAndTagsModal = document.getElementById('categoriesAndTagsModal') as HTMLElement;
        this.imagePreview = document.getElementById('image-preview') as HTMLImageElement;

        this.subRecipesModal = document.getElementById('subRecipesModal') as HTMLElement;
        this.subRecipesButton = document.getElementById('subRecipeButton') as HTMLButtonElement;
        console.log("subRecipesModal", this.subRecipesModal);
        console.log("subRecipesButton", this.subRecipesButton);


        if(this.mainForm){
            this.setupListenersForRecipeForm();
            new IngredientsAndStepsManager(this.mainForm);
        }        
    }

    setupListenersForRecipeForm(): void { // Revisit to simplify
        if(this.mainForm){

            const dropdownButton = this.mainForm.querySelector<HTMLButtonElement>('#subRecipeDropdown');
            const dropdownMenu = this.mainForm.querySelector<HTMLElement>('#subRecipeDropdownMenu');
            
            if (dropdownButton && dropdownMenu) {
                dropdownButton.addEventListener("click", function (event) {
                    event.stopPropagation(); // Prevents clicks inside menu from closing it
                    dropdownMenu.classList.toggle("show");
                    });
                }
            }
            if(this.categoriesAndTagsModal){


                if(this.mainForm?.action.includes('update')){
                   
                    // Add a listener for categories and tags button
                    const categoriesAndTagsButton = this.mainForm.querySelector<HTMLButtonElement>('#openCategoriesAndTagsButton');
                   
                    if (categoriesAndTagsButton && !this.initialeSelectionsLoaded) {
                        categoriesAndTagsButton.addEventListener('click', () => {
                        
                            this.loadCategoriesAndTagsInitialSelections();});

                            // Load initial selections only once
                            this.initialeSelectionsLoaded = true;
                        }
                    }

            this.categoriesAndTagsModal.addEventListener('change', (event)=> {
                const target = event.target as HTMLInputElement;
                if(target.type == 'checkbox'){
                    const value = parseInt(target.value);
                    if(target.id.startsWith('id_categories_')){
                        if(target.checked){
                            this.selectedCategories.add(value);
                        }
                        else {
                            this.selectedCategories.delete(value);
                        }
                    }
                    else if(target.id.startsWith('id_tags_')){
                        if(target.checked){
                            this.selectedTags.add(value);
                        }
                        else{
                            this.selectedTags.delete(value);
                        }
                    }
                }
            });
            // Update selections when modal is hidden
            this.categoriesAndTagsModal.addEventListener('hidden.bs.modal', () => {
                this.updateFormSelections();
            });

            if(this.imagePreview && this.mainForm){
                const fileInput = this.mainForm.querySelector<HTMLInputElement>('input[id="id_picture"]');
                if(fileInput){
                    fileInput.addEventListener('change', () => {
                        RecipeManager.previewImage(fileInput, this.imagePreview);
                    });
                }
            }

            if(this.subRecipesModal && this.subRecipesButton){
                this.subRecipesButton.addEventListener('click', () => {
                    // Load initial selections for sub-recipes
                    if (!this.initialSubRecipeSelectionLoaded) {
                        this.loadInitialSubRecipeSelections();
                        this.initialSubRecipeSelectionLoaded = true;
                    }
                });

                // Handle sub-recipe selection changes
                this.subRecipesModal.addEventListener('change', (event) => {
                    const target = event.target as HTMLInputElement;
                    if (target.type === 'checkbox' && target.id.startsWith('id_sub_recipes_')) {
                        const value = parseInt(target.value);
                        if (target.checked) {
                            this.selectedSubRecipes.add(value);
                        } else {
                            this.selectedSubRecipes.delete(value);
                        }
                    }
                });

                // Update selections when modal is hidden
                this.subRecipesModal.addEventListener('hidden.bs.modal', () => {
                    this.updateSubRecipeSelections();
                });
            }
        }  
    }

    private loadInitialSubRecipeSelections(): void {
        if (!this.subRecipesModal) {
            return;
        }
        // Load initial state from form
        const subRecipeInputs = this.subRecipesModal.querySelectorAll<HTMLInputElement>('input[id^="id_sub_recipes_"]');
        subRecipeInputs.forEach(input => {
            if (input.checked) {
                this.selectedSubRecipes.add(parseInt(input.value));
            }
        });
    }

    private updateSubRecipeSelections(): void {
        if (!this.mainForm) return;

        // Remove old hidden inputs
        this.mainForm.querySelectorAll('input[name="sub_recipes"]').forEach(input => input.remove());

        // Add new hidden inputs for sub-recipes
        const subRecipesContainer = this.mainForm.querySelector<HTMLElement>('#sub-recipes-hidden');
        if (subRecipesContainer) {
            RecipeManager.addHiddenInputs(subRecipesContainer, this.selectedSubRecipes, 'sub_recipes');
        }
    }


    private loadCategoriesAndTagsInitialSelections(): void {

        if (!this.categoriesAndTagsModal) {
            return;
        }
        // Load initial state from form
        const categoryInputs = this.categoriesAndTagsModal.querySelectorAll<HTMLInputElement>('input[id^="id_categories_"]');
        const tagInputs = this.categoriesAndTagsModal.querySelectorAll<HTMLInputElement>('input[id^="id_tags_"]');


        categoryInputs.forEach(input => {
            if (input.checked) {
                this.selectedCategories.add(parseInt(input.value));
            }
        });

        tagInputs.forEach(input => {
            if (input.checked) {
                this.selectedTags.add(parseInt(input.value));
            }
        });
    }

    

    private updateFormSelections(): void {
        if (!this.mainForm) return;

        // Remove old hidden inputs
        this.mainForm.querySelectorAll('input[name="categories"], input[name="tags"]').forEach(input => input.remove());
        
        // Add new hidden inputs for categories
        const categoriesContainer = this.mainForm.querySelector<HTMLElement>('#categories-hidden');
        if (categoriesContainer) {
            RecipeManager.addHiddenInputs(categoriesContainer, this.selectedCategories, elementIdentifier.CATEGORIES);
        }
        // Add new hidden inputs for tags
        const tagsContainer = this.mainForm.querySelector<HTMLElement>('#tags-hidden');
        if (tagsContainer) {
            RecipeManager.addHiddenInputs(tagsContainer,this.selectedTags, elementIdentifier.TAGS);
        }
    }

    private static addHiddenInputs(checkboxes: HTMLElement,selectedElements: Set<number>, elementIdentifier: string): void {
        selectedElements.forEach(id => {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = `${elementIdentifier}`;
        input.value = id.toString();
        checkboxes?.appendChild(input);
        });
    }

    private static previewImage(fileInput: HTMLInputElement, imagePreview: HTMLImageElement | null): void {
        if (!fileInput || !imagePreview) {
            return;
        }
        
        const file = fileInput.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(event) {
                if (event.target && event.target.result) {
                    imagePreview.src = event.target.result as string;
                    imagePreview.style.display = 'block';
                }
            };
            reader.readAsDataURL(file);
        } else {
            imagePreview.src = '';
            imagePreview.style.display = 'none';
        }
    }
}
