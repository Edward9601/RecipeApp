enum elementIdentifier {
    CATEGORIES = 'categories',
    TAGS = 'tags'

}
class RecipeManager {

    private static instance: RecipeManager;
    private mainForm: HTMLFormElement | null = null;

    // Cattegories and tags block
    // Using Sets to avoid duplicates and for easier management
    private selectedCategories: Set<number> = new Set();
    private selectedTags: Set<number> = new Set();

    private categoriesAndTagsModal: HTMLElement | null = null;
    // Flag to ensure initial selections are loaded only once
    private initialeSelectionsLoaded: boolean = false;

    // Ingredients and Steps formset management
    private addIngredientButton: HTMLButtonElement | null = null;
    private addStepButton: HTMLButtonElement | null = null;

    
    
    private constructor() {
        this.mainForm = document.getElementById('recipe-from') as HTMLFormElement;
        this.categoriesAndTagsModal = document.getElementById('categoriesAndTagsModal');
        this.addIngredientButton = document.getElementById('addIngredientButton') as HTMLButtonElement;
        this.addStepButton = document.getElementById('add-step-button') as HTMLButtonElement;
        console.log('Found main form:', this.mainForm !== null);
        this.setupListeners();
    }

    static getInstance(): RecipeManager {
        if (!RecipeManager.instance) {
            RecipeManager.instance = new RecipeManager();
        }
        return RecipeManager.instance;
    }

    setupListeners(): void { // Revisit to simplify
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
            this.addIngredientButton?.addEventListener('click', (event) => {
                event.preventDefault();
                console.log('Add ingredient button clicked');
                this.addIngredientForm();
            }); 

            this.addStepButton?.addEventListener('click', (event) => {
                event.preventDefault();
                console.log('Add step button clicked');
                this.addStepForm();
            });

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


    // Ingredients and Steps formset management
    private addIngredientForm(): void {
        if(!this.mainForm){
            console.error('Main form is not initialized.')
            return;
        }

        let formsetDiv = this.mainForm.querySelector<HTMLElement>('#ingredient-formset');

        let totalFormsInput = this.mainForm.querySelector<HTMLInputElement>('#id_ingredients-TOTAL_FORMS');

        if (!formsetDiv || !totalFormsInput) {
            console.error('Formset div or TOTAL_FORMS input not found.');
            return;
        }
        // Get the current total number of forms
        let totalForms = parseInt(totalFormsInput.value, 10);

        // Get the empty form template, then clone the empty form
        let emptyFormTemplate = this.mainForm.querySelector<HTMLElement>('#empty-ingredient-form');
        if (!emptyFormTemplate) {
            console.error('Empty form template not found.');
            return;
        }
        const newForm = emptyFormTemplate.cloneNode(true) as HTMLElement;
        newForm.classList.add('ingredient-form');
        newForm.removeAttribute('id');
        newForm.style.removeProperty('display');
        newForm.innerHTML = newForm.innerHTML.replace(/__prefix__/g, totalForms.toString());

        formsetDiv.appendChild(newForm);

        totalFormsInput.value = (totalForms + 1).toString();
    }
    
    private addStepForm(): void {
        if (!this.mainForm) {
            console.error('Main form is not initialized.');
            return;
        }
        const mainForm = this.mainForm;
        let formsetDiv = mainForm.querySelector<HTMLElement>('#step-formset');
        let totalFormsInput = mainForm.querySelector<HTMLInputElement>('#id_steps-TOTAL_FORMS');
        if (!formsetDiv || !totalFormsInput) {
            console.error('Formset div or TOTAL_FORMS input not found.');
            return;
        }
        let totalForms = parseInt(totalFormsInput.value, 10);

        // Get the empty form template and clone it
        let emptyFormTemplate = mainForm.querySelector<HTMLElement>('#empty-step-form');
        if (!emptyFormTemplate) {
            console.error('Empty form template not found.');
            return;
        }
        const newForm = emptyFormTemplate.cloneNode(true) as HTMLElement;
        newForm.classList.add('step-form');
        newForm.removeAttribute('id');
        newForm.style.removeProperty('display');

        const updatedHTML = newForm.innerHTML.replace(/__prefix__/g, totalForms.toString());

        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = updatedHTML;

        const orderInput = tempDiv.querySelector<HTMLInputElement>('input[name$="-order"]');
        if (orderInput) {
            orderInput.value = (totalForms + 1).toString();
        }

        newForm.innerHTML = tempDiv.innerHTML;
        formsetDiv.appendChild(newForm);

        totalFormsInput.value = (totalForms + 1).toString();
    }
}

// Initialize when the document loads
document.addEventListener('DOMContentLoaded', () => {
    RecipeManager.getInstance();
});