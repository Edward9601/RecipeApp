"use strict";
var elementIdentifier;
(function (elementIdentifier) {
    elementIdentifier["CATEGORIES"] = "categories";
    elementIdentifier["TAGS"] = "tags";
})(elementIdentifier || (elementIdentifier = {}));
class RecipeManager {
    constructor() {
        this.mainForm = null;
        // Cattegories and tags block
        // Using Sets to avoid duplicates and for easier management
        this.selectedCategories = new Set();
        this.selectedTags = new Set();
        this.categoriesAndTagsModal = null;
        this.initialeSelectionsLoaded = false;
        // Ingredients and Steps formset management
        this.addIngredientButton = null;
        this.addStepButton = null;
        this.mainForm = document.getElementById('recipe-from');
        this.categoriesAndTagsModal = document.getElementById('categoriesAndTagsModal');
        this.addIngredientButton = document.getElementById('addIngredientButton');
        this.addStepButton = document.getElementById('add-step-button');
        console.log('Found main form:', this.mainForm !== null);
        this.setupListeners();
    }
    static getInstance() {
        if (!RecipeManager.instance) {
            RecipeManager.instance = new RecipeManager();
        }
        return RecipeManager.instance;
    }
    setupListeners() {
        var _a, _b, _c;
        console.log('Setting up listeners');
        if (this.mainForm) {
            const dropdownButton = this.mainForm.querySelector('#subRecipeDropdown');
            const dropdownMenu = this.mainForm.querySelector('#subRecipeDropdownMenu');
            if (dropdownButton && dropdownMenu) {
                dropdownButton.addEventListener("click", function (event) {
                    event.stopPropagation(); // Prevents clicks inside menu from closing it
                    dropdownMenu.classList.toggle("show");
                });
            }
        }
        (_a = this.addIngredientButton) === null || _a === void 0 ? void 0 : _a.addEventListener('click', (event) => {
            event.preventDefault();
            console.log('Add ingredient button clicked');
            this.addIngredientForm();
        });
        (_b = this.addStepButton) === null || _b === void 0 ? void 0 : _b.addEventListener('click', (event) => {
            event.preventDefault();
            console.log('Add step button clicked');
            this.addStepForm();
        });
        if (this.categoriesAndTagsModal) {
            if ((_c = this.mainForm) === null || _c === void 0 ? void 0 : _c.action.includes('update')) {
                console.log('Main form is for updating, loading initial selections');
                // Add a listener for categories and tags button
                const categoriesAndTagsButton = this.mainForm.querySelector('#openCategoriesAndTagsButton');
                console.log('Found categories and tags button:', categoriesAndTagsButton !== null);
                if (categoriesAndTagsButton && !this.initialeSelectionsLoaded) {
                    categoriesAndTagsButton.addEventListener('click', () => {
                        console.log('Categories and Tags button clicked');
                        this.loadInitialSelections();
                    });
                    // Load initial selections only once
                    this.initialeSelectionsLoaded = true;
                }
            }
            this.categoriesAndTagsModal.addEventListener('change', (event) => {
                const target = event.target;
                if (target.type == 'checkbox') {
                    const value = parseInt(target.value);
                    if (target.id.startsWith('id_categories_')) {
                        if (target.checked) {
                            this.selectedCategories.add(value);
                        }
                        else {
                            this.selectedCategories.delete(value);
                        }
                        console.log('Categories updated:', Array.from(this.selectedCategories));
                    }
                    else if (target.id.startsWith('id_tags_')) {
                        if (target.checked) {
                            this.selectedTags.add(value);
                        }
                        else {
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
    loadInitialSelections() {
        if (!this.categoriesAndTagsModal) {
            console.warn('Modal not found. Cannot load initial selections.');
            return;
        }
        console.log('Loading initial selections');
        // Load initial state from form
        const categoryInputs = this.categoriesAndTagsModal.querySelectorAll('input[id^="id_categories_"]');
        const tagInputs = this.categoriesAndTagsModal.querySelectorAll('input[id^="id_tags_"]');
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
    updateFormSelections() {
        if (!this.mainForm)
            return;
        // Remove old hidden inputs
        this.mainForm.querySelectorAll('input[name="categories"], input[name="tags"]').forEach(input => input.remove());
        // Add new hidden inputs for categories
        const categoriesContainer = this.mainForm.querySelector('#categories-hidden');
        if (categoriesContainer) {
            RecipeManager.addHiddenInputs(categoriesContainer, this.selectedCategories, elementIdentifier.CATEGORIES);
        }
        // Add new hidden inputs for tags
        const tagsContainer = this.mainForm.querySelector('#tags-hidden');
        if (tagsContainer) {
            RecipeManager.addHiddenInputs(tagsContainer, this.selectedTags, elementIdentifier.TAGS);
        }
    }
    static addHiddenInputs(checkboxes, selectedElements, elementIdentifier) {
        selectedElements.forEach(id => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = `${elementIdentifier}`;
            input.value = id.toString();
            checkboxes === null || checkboxes === void 0 ? void 0 : checkboxes.appendChild(input);
        });
        console.log('Hidden inputs updated:', Array.from(selectedElements));
    }
    // Ingredients and Steps formset management
    addIngredientForm() {
        if (!this.mainForm) {
            console.error('Main form is not initialized.');
            return;
        }
        let formsetDiv = this.mainForm.querySelector('#ingredient-formset');
        let totalFormsInput = this.mainForm.querySelector('#id_ingredients-TOTAL_FORMS');
        if (!formsetDiv || !totalFormsInput) {
            console.error('Formset div or TOTAL_FORMS input not found.');
            return;
        }
        // Get the current total number of forms
        let totalForms = parseInt(totalFormsInput.value, 10);
        // Get the empty form template, then clone the empty form
        let emptyFormTemplate = this.mainForm.querySelector('#empty-ingredient-form');
        if (!emptyFormTemplate) {
            console.error('Empty form template not found.');
            return;
        }
        const newForm = emptyFormTemplate.cloneNode(true);
        newForm.classList.add('ingredient-form');
        newForm.removeAttribute('id');
        newForm.style.removeProperty('display');
        newForm.innerHTML = newForm.innerHTML.replace(/__prefix__/g, totalForms.toString());
        formsetDiv.appendChild(newForm);
        totalFormsInput.value = (totalForms + 1).toString();
    }
    addStepForm() {
        if (!this.mainForm) {
            console.error('Main form is not initialized.');
            return;
        }
        const mainForm = this.mainForm;
        let formsetDiv = mainForm.querySelector('#step-formset');
        let totalFormsInput = mainForm.querySelector('#id_steps-TOTAL_FORMS');
        if (!formsetDiv || !totalFormsInput) {
            console.error('Formset div or TOTAL_FORMS input not found.');
            return;
        }
        let totalForms = parseInt(totalFormsInput.value, 10);
        // Get the empty form template and clone it
        let emptyFormTemplate = mainForm.querySelector('#empty-step-form');
        if (!emptyFormTemplate) {
            console.error('Empty form template not found.');
            return;
        }
        const newForm = emptyFormTemplate.cloneNode(true);
        newForm.classList.add('step-form');
        newForm.removeAttribute('id');
        newForm.style.removeProperty('display');
        const updatedHTML = newForm.innerHTML.replace(/__prefix__/g, totalForms.toString());
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = updatedHTML;
        const orderInput = tempDiv.querySelector('input[name$="-order"]');
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
//# sourceMappingURL=recipes.js.map