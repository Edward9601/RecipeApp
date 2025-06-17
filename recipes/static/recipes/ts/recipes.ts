interface CategoryTag {
    id: number;
    name: string;
}

class CategoryTagManager {

    private static instance: CategoryTagManager;
    private selectedCategories: Set<number> = new Set();
    private selectedTags: Set<number> = new Set();
    private mainForm: HTMLFormElement | null = null;
    
    private constructor() {
        console.log('Constructor called');
        this.mainForm = document.querySelector('form');
        console.log('Found main form:', this.mainForm !== null);
        this.loadInitialSelections();
        this.setupListeners();
    }

    static getInstance(): CategoryTagManager {
        if (!CategoryTagManager.instance) {
            CategoryTagManager.instance = new CategoryTagManager();
        }
        return CategoryTagManager.instance;
    }

    private loadInitialSelections(): void {
        console.log('Loading initial selections');
        // Load initial state from form
        const categoryInputs = document.querySelectorAll<HTMLInputElement>('input[id^="id_categories_"]');
        const tagInputs = document.querySelectorAll<HTMLInputElement>('input[id^="id_tags_"]');

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

    setupListeners(): void {
        console.log('Setting up listeners');
        
        // Listen for changes on any checkbox in the modal
        const modal = document.getElementById('categoriesAndTagsModal');
        if (modal) {
            modal.addEventListener('change', (e) => {
                const target = e.target as HTMLInputElement;
                if (target.type === 'checkbox') {
                    const value = parseInt(target.value);
                    
                    if (target.id.startsWith('id_categories_')) {
                        if (target.checked) {
                            this.selectedCategories.add(value);
                        } else {
                            this.selectedCategories.delete(value);
                        }
                        console.log('Categories updated:', Array.from(this.selectedCategories));
                    }
                    else if (target.id.startsWith('id_tags_')) {
                        if (target.checked) {
                            this.selectedTags.add(value);
                        } else {
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

    private updateFormSelections(): void {
        console.log('Updating selections:', {
            categories: Array.from(this.selectedCategories),
            tags: Array.from(this.selectedTags)
        });

        if (!this.mainForm) {
            console.error('Main form not found');
            return;
        }

        // Update main form category checkboxes
        const mainFormCategoryInputs = this.mainForm.querySelectorAll<HTMLInputElement>('input[id^="id_categories_"]');
        mainFormCategoryInputs.forEach(input => {
            const value = parseInt(input.value);
            input.checked = this.selectedCategories.has(value);
        });

        // Update main form tag checkboxes
        const mainFormTagInputs = this.mainForm.querySelectorAll<HTMLInputElement>('input[id^="id_tags_"]');
        mainFormTagInputs.forEach(input => {
            const value = parseInt(input.value);
            input.checked = this.selectedTags.has(value);
        });

        // Update modal checkboxes to match
        document.querySelectorAll<HTMLInputElement>('input[id^="id_categories_"]').forEach(checkbox => {
            const value = parseInt(checkbox.value);
            checkbox.checked = this.selectedCategories.has(value);
        });

        document.querySelectorAll<HTMLInputElement>('input[id^="id_tags_"]').forEach(checkbox => {
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