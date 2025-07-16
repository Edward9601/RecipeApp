import { IngredientsAndStepsManager } from './ingredients_and_steps.js';
var elementIdentifier;
(function (elementIdentifier) {
    elementIdentifier["CATEGORIES"] = "categories";
    elementIdentifier["TAGS"] = "tags";
})(elementIdentifier || (elementIdentifier = {}));
export class RecipeManager {
    constructor() {
        this.mainForm = null;
        // Cattegories and tags block
        // Using Sets to avoid duplicates and for easier management
        this.selectedCategories = new Set();
        this.selectedTags = new Set();
        this.categoriesAndTagsModal = null;
        // Flag to ensure initial selections are loaded only once
        this.initialeSelectionsLoaded = false;
        this.subRecipesModal = null;
        this.subRecipesButton = null;
        this.selectedSubRecipes = new Set();
        this.initialSubRecipeSelectionLoaded = false;
        this.imagePreview = null;
        this.mainForm = document.getElementById('recipe-form');
        this.categoriesAndTagsModal = document.getElementById('categoriesAndTagsModal');
        this.imagePreview = document.getElementById('image-preview');
        this.subRecipesModal = document.getElementById('subRecipesModal');
        this.subRecipesButton = document.getElementById('subRecipeButton');
        console.log("subRecipesModal", this.subRecipesModal);
        console.log("subRecipesButton", this.subRecipesButton);
        if (this.mainForm) {
            this.setupListenersForRecipeForm();
            new IngredientsAndStepsManager(this.mainForm);
        }
    }
    setupListenersForRecipeForm() {
        var _a;
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
        if (this.categoriesAndTagsModal) {
            if ((_a = this.mainForm) === null || _a === void 0 ? void 0 : _a.action.includes('update')) {
                // Add a listener for categories and tags button
                const categoriesAndTagsButton = this.mainForm.querySelector('#openCategoriesAndTagsButton');
                if (categoriesAndTagsButton && !this.initialeSelectionsLoaded) {
                    categoriesAndTagsButton.addEventListener('click', () => {
                        this.loadCategoriesAndTagsInitialSelections();
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
                    }
                    else if (target.id.startsWith('id_tags_')) {
                        if (target.checked) {
                            this.selectedTags.add(value);
                        }
                        else {
                            this.selectedTags.delete(value);
                        }
                    }
                }
            });
            // Update selections when modal is hidden
            this.categoriesAndTagsModal.addEventListener('hidden.bs.modal', () => {
                this.updateFormSelections();
            });
            if (this.imagePreview && this.mainForm) {
                const fileInput = this.mainForm.querySelector('input[id="id_picture"]');
                if (fileInput) {
                    fileInput.addEventListener('change', () => {
                        RecipeManager.previewImage(fileInput, this.imagePreview);
                    });
                }
            }
            if (this.subRecipesModal && this.subRecipesButton) {
                this.subRecipesButton.addEventListener('click', () => {
                    // Load initial selections for sub-recipes
                    if (!this.initialSubRecipeSelectionLoaded) {
                        this.loadInitialSubRecipeSelections();
                        this.initialSubRecipeSelectionLoaded = true;
                    }
                });
                // Handle sub-recipe selection changes
                this.subRecipesModal.addEventListener('change', (event) => {
                    const target = event.target;
                    if (target.type === 'checkbox' && target.id.startsWith('id_sub_recipes_')) {
                        const value = parseInt(target.value);
                        if (target.checked) {
                            this.selectedSubRecipes.add(value);
                        }
                        else {
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
    loadInitialSubRecipeSelections() {
        if (!this.subRecipesModal) {
            return;
        }
        // Load initial state from form
        const subRecipeInputs = this.subRecipesModal.querySelectorAll('input[id^="id_sub_recipes_"]');
        subRecipeInputs.forEach(input => {
            if (input.checked) {
                this.selectedSubRecipes.add(parseInt(input.value));
            }
        });
    }
    updateSubRecipeSelections() {
        if (!this.mainForm)
            return;
        // Remove old hidden inputs
        this.mainForm.querySelectorAll('input[name="sub_recipes"]').forEach(input => input.remove());
        // Add new hidden inputs for sub-recipes
        const subRecipesContainer = this.mainForm.querySelector('#sub-recipes-hidden');
        if (subRecipesContainer) {
            RecipeManager.addHiddenInputs(subRecipesContainer, this.selectedSubRecipes, 'sub_recipes');
        }
    }
    loadCategoriesAndTagsInitialSelections() {
        if (!this.categoriesAndTagsModal) {
            return;
        }
        // Load initial state from form
        const categoryInputs = this.categoriesAndTagsModal.querySelectorAll('input[id^="id_categories_"]');
        const tagInputs = this.categoriesAndTagsModal.querySelectorAll('input[id^="id_tags_"]');
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
    }
    static previewImage(fileInput, imagePreview) {
        var _a;
        if (!fileInput || !imagePreview) {
            return;
        }
        const file = (_a = fileInput.files) === null || _a === void 0 ? void 0 : _a[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (event) {
                if (event.target && event.target.result) {
                    imagePreview.src = event.target.result;
                    imagePreview.style.display = 'block';
                }
            };
            reader.readAsDataURL(file);
        }
        else {
            imagePreview.src = '';
            imagePreview.style.display = 'none';
        }
    }
}
//# sourceMappingURL=recipes.js.map