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
        if (this.mainForm) {
            this.setupListenersForRecipeForm(this.mainForm);
        }
    }
    setupListenersForRecipeForm(mainForm) {
        const dropdownButton = mainForm.querySelector('#subRecipeDropdown');
        const dropdownMenu = mainForm.querySelector('#subRecipeDropdownMenu');
        if (dropdownButton && dropdownMenu) {
            dropdownButton.addEventListener("click", (event) => {
                event.stopPropagation(); // Prevents clicks inside menu from closing it
                dropdownMenu.classList.toggle("show");
            });
        }
        if (this.categoriesAndTagsModal) {
            if (mainForm.action.includes('update')) {
                // Add a listener for categories and tags button
                const categoriesAndTagsButton = mainForm.querySelector('#openCategoriesAndTagsButton');
                if (categoriesAndTagsButton && !this.initialeSelectionsLoaded) {
                    categoriesAndTagsButton.addEventListener('click', () => {
                        // We are sure that categoriesAndTagsModal isn't null, thus "!"
                        this.loadCategoriesAndTagsInitialSelections(this.categoriesAndTagsModal);
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
        }
        if (this.imagePreview) {
            const fileInput = mainForm.querySelector('input[id="id_picture"]');
            if (fileInput) {
                fileInput.addEventListener('change', () => {
                    RecipeManager.previewImage(fileInput, this.imagePreview);
                });
            }
        }
        if (this.subRecipesModal) {
            // Load initial selections for sub-recipes
            if (!this.initialSubRecipeSelectionLoaded && this.subRecipesButton) {
                this.subRecipesButton.addEventListener('click', () => {
                    this.loadInitialSubRecipeSelections(this.subRecipesModal);
                    this.initialSubRecipeSelectionLoaded = true;
                });
            }
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
                this.updateSubRecipeSelections(mainForm);
            });
        }
    }
    loadInitialSubRecipeSelections(subRecipesModal) {
        // Load initial state from form
        const subRecipeInputs = subRecipesModal.querySelectorAll('input[id^="id_sub_recipes_"]');
        subRecipeInputs.forEach(input => {
            if (input.checked) {
                this.selectedSubRecipes.add(parseInt(input.value));
            }
        });
    }
    updateSubRecipeSelections(mainForm) {
        // Remove old hidden inputs
        mainForm.querySelectorAll('input[name="sub_recipes"]').forEach(input => input.remove());
        // Add new hidden inputs for sub-recipes
        const subRecipesContainer = mainForm.querySelector('#sub-recipes-hidden');
        if (subRecipesContainer) {
            RecipeManager.addHiddenInputs(subRecipesContainer, this.selectedSubRecipes, 'sub_recipes');
        }
    }
    loadCategoriesAndTagsInitialSelections(categoriesAndTagsModal) {
        // Load initial state from form
        const categoryInputs = categoriesAndTagsModal.querySelectorAll('input[id^="id_categories_"]');
        const tagInputs = categoriesAndTagsModal.querySelectorAll('input[id^="id_tags_"]');
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