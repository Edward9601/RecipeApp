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

    
    constructor() {
        this.mainForm = document.getElementById('recipe-form') as HTMLFormElement;
        this.categoriesAndTagsModal = document.getElementById('categoriesAndTagsModal');

        if(this.mainForm){
            this.setupListenersForRecipeForm();
            new IngredientsAndStepsManager(this.mainForm);
        }        
    }

    setupListenersForRecipeForm(): void { // Revisit to simplify
        console.log('Setting up listeners');
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
                    console.log('Main form is for updating, loading initial selections');
                    // Add a listener for categories and tags button
                    const categoriesAndTagsButton = this.mainForm.querySelector<HTMLButtonElement>('#openCategoriesAndTagsButton');
                    console.log('Found categories and tags button:', categoriesAndTagsButton !== null);
                    if (categoriesAndTagsButton && !this.initialeSelectionsLoaded) {
                        categoriesAndTagsButton.addEventListener('click', () => {
                            console.log('Categories and Tags button clicked');
                            this.loadInitialSelections();});

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
                        console.log('Categories updated:', Array.from(this.selectedCategories));
                    }
                    else if(target.id.startsWith('id_tags_')){
                        if(target.checked){
                            this.selectedTags.add(value);
                        }
                        else{
                            this.selectedTags.delete(value);
                        }
                        console.log('Tags updated:', Array.from(this.selectedTags));
                    }
                }
            });
            // Update selections when modal is hidden
            this.categoriesAndTagsModal.addEventListener('hidden.bs.modal', () => {
                console.log('Modal hidden, updating selections');
                this.updateFormSelections();
            });
        }  
    }

    private loadInitialSelections(): void {

        if (!this.categoriesAndTagsModal) {
            console.warn('Modal not found. Cannot load initial selections.');
            return;
        }
        console.log('Loading initial selections');
        // Load initial state from form
        const categoryInputs = this.categoriesAndTagsModal.querySelectorAll<HTMLInputElement>('input[id^="id_categories_"]');
        const tagInputs = this.categoriesAndTagsModal.querySelectorAll<HTMLInputElement>('input[id^="id_tags_"]');

        console.log(`Found ${categoryInputs.length} category inputs and ${tagInputs.length} tag inputs`);

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
        console.log('Hidden inputs updated:', Array.from(selectedElements));
    }
}
