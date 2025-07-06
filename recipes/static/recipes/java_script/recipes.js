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
        this.imagePreview = null;
        this.mainForm = document.getElementById('recipe-form');
        this.categoriesAndTagsModal = document.getElementById('categoriesAndTagsModal');
        this.imagePreview = document.getElementById('image-preview');
        if (this.mainForm) {
            this.setupListenersForRecipeForm();
            new IngredientsAndStepsManager(this.mainForm);
        }
    }
    setupListenersForRecipeForm() {
        var _a;
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
        if (this.categoriesAndTagsModal) {
            if ((_a = this.mainForm) === null || _a === void 0 ? void 0 : _a.action.includes('update')) {
                // Add a listener for categories and tags button
                const categoriesAndTagsButton = this.mainForm.querySelector('#openCategoriesAndTagsButton');
                if (categoriesAndTagsButton && !this.initialeSelectionsLoaded) {
                    categoriesAndTagsButton.addEventListener('click', () => {
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
            if (this.imagePreview && this.mainForm) {
                const fileInput = this.mainForm.querySelector('input[id="id_picture"]');
                if (fileInput) {
                    fileInput.addEventListener('change', () => {
                        RecipeManager.previewImage(fileInput, this.imagePreview);
                    });
                }
            }
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
    static previewImage(fileInput, imagePreview) {
        var _a;
        if (!fileInput || !imagePreview) {
            console.error('File input or image preview element not found.');
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