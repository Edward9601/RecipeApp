"use strict";
class CategoryTagManager {
    constructor() {
        this.selectedCategories = new Set();
        this.selectedTags = new Set();
        this.mainForm = null;
        console.log('Constructor called');
        this.mainForm = document.querySelector('form');
        console.log('Found main form:', this.mainForm !== null);
        this.loadInitialSelections();
        this.setupListeners();
    }
    static getInstance() {
        if (!CategoryTagManager.instance) {
            CategoryTagManager.instance = new CategoryTagManager();
        }
        return CategoryTagManager.instance;
    }
    loadInitialSelections() {
        console.log('Loading initial selections');
        // Load initial state from form
        const categoryInputs = document.querySelectorAll('input[id^="id_categories_"]');
        const tagInputs = document.querySelectorAll('input[id^="id_tags_"]');
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
    setupListeners() {
        console.log('Setting up listeners');
        // Listen for changes on any checkbox in the modal
        const modal = document.getElementById('categoriesAndTagsModal');
        if (modal) {
            modal.addEventListener('change', (e) => {
                const target = e.target;
                if (target.type === 'checkbox') {
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
            modal.addEventListener('hidden.bs.modal', () => {
                console.log('Modal hidden, updating selections');
                this.updateFormSelections();
            });
        }
    }
    updateFormSelections() {
        console.log('Updating selections:', {
            categories: Array.from(this.selectedCategories),
            tags: Array.from(this.selectedTags)
        });
        if (!this.mainForm) {
            console.error('Main form not found');
            return;
        }
        // Update main form category checkboxes
        const mainFormCategoryInputs = this.mainForm.querySelectorAll('input[id^="id_categories_"]');
        mainFormCategoryInputs.forEach(input => {
            const value = parseInt(input.value);
            input.checked = this.selectedCategories.has(value);
        });
        // Update main form tag checkboxes
        const mainFormTagInputs = this.mainForm.querySelectorAll('input[id^="id_tags_"]');
        mainFormTagInputs.forEach(input => {
            const value = parseInt(input.value);
            input.checked = this.selectedTags.has(value);
        });
        // Update modal checkboxes to match
        document.querySelectorAll('input[id^="id_categories_"]').forEach(checkbox => {
            const value = parseInt(checkbox.value);
            checkbox.checked = this.selectedCategories.has(value);
        });
        document.querySelectorAll('input[id^="id_tags_"]').forEach(checkbox => {
            const value = parseInt(checkbox.value);
            checkbox.checked = this.selectedTags.has(value);
        });
        console.log('Form updated with selections');
    }
}
// Initialize when the document loads
document.addEventListener('DOMContentLoaded', () => {
    CategoryTagManager.getInstance();
});
//# sourceMappingURL=recipes.js.map