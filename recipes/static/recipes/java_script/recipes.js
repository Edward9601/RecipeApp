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
        this.filtersButton = null;
        this.filtersPanel = null;
        this.mainForm = document.getElementById('recipe-form');
        this.categoriesAndTagsModal = document.getElementById('categoriesAndTagsModal');
        this.filtersButton = document.getElementById('filterDropdownBtn');
        this.filtersPanel = document.getElementById('filterDropdownPanel');
        if (this.mainForm) {
            this.setupListenersForRecipeForm();
            new IngredientsAndStepsManager(this.mainForm);
        }
        if (this.filtersButton) {
            this.setupFiltersButton();
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
    setupFiltersButton() {
        if (!this.filtersButton || !this.filtersPanel) {
            console.error('Filters button or panel not found.');
            return;
        }
        this.filtersButton.addEventListener('click', (event) => {
            var _a, _b, _c, _d;
            event.stopPropagation();
            if (!((_a = this.filtersPanel) === null || _a === void 0 ? void 0 : _a.classList.contains('open'))) {
                (_b = this.filtersPanel) === null || _b === void 0 ? void 0 : _b.classList.add('open');
                (_c = this.filtersButton) === null || _c === void 0 ? void 0 : _c.setAttribute('aria-expanded', 'true');
            }
            else {
                this.filtersPanel.classList.remove('open');
                (_d = this.filtersButton) === null || _d === void 0 ? void 0 : _d.setAttribute('aria-expanded', 'false');
            }
        });
        document.addEventListener('click', (event) => {
            var _a, _b, _c, _d;
            if (!((_a = this.filtersButton) === null || _a === void 0 ? void 0 : _a.contains(event.target)) &&
                !((_b = this.filtersPanel) === null || _b === void 0 ? void 0 : _b.contains(event.target))) {
                (_c = this.filtersPanel) === null || _c === void 0 ? void 0 : _c.classList.remove('open');
                (_d = this.filtersButton) === null || _d === void 0 ? void 0 : _d.setAttribute('aria-expanded', 'false');
            }
        });
    }
}
//# sourceMappingURL=recipes.js.map