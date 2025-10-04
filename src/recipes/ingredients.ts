
import { Ingredient } from "./interfaces/recipe_items_interfaces.js";
import { BaseFormManager } from "./base_recipe_item.js";
import { FormManagerConfig } from './interfaces/recipe_items_interfaces.js'
import { RecipeManager } from "./recipes.js";

export class IngredientsManager extends BaseFormManager<Ingredient> {

    constructor(config: FormManagerConfig) {
        super(config);
        this.SetUpActionButtonsModalEventListener();
    }

    private SetUpActionButtonsModalEventListener(){
        if (this.addButton) {
            this.addButton.addEventListener('click', (event) => {
                event.preventDefault();
                this.addItemToForm();
            });
        }
        
        if (this.saveButton) {
            this.saveButton.addEventListener('click', (event) => {
                event.preventDefault();
                if (this.isUpdateMode) {
                    const apiUrl = this.saveButton.dataset.url!;
                    this.handleUpdateSave(apiUrl);
                    this.closeModal(this.htmlModal);
                } else {
                    this.handleCreateSave();
                    this.closeModal(this.htmlModal);
                }
            });
        }
    }

    protected override setUpButtonsDelegationEventListeners(): void {
        const itemList = this.htmlModal.querySelector('#ingredients-list') as HTMLElement;
        if (itemList) {
            itemList.addEventListener('click', (event) => {
                const target = event.target as HTMLElement;
                if (target.matches('.remove-button')) {
                    event.preventDefault();
                    this.removeItemForm(target);
                }
                if(target.matches('.undo-btn')){
                    event.preventDefault();
                    this.undoRemoveItemForm(target);
                }
            });
        } else {
            console.error(`${this.config.fieldPrefix}s list not found.`);
        }
    }

    private undoRemoveItemForm(button: HTMLElement): void {
        const itemCard = button.closest(`.${this.config.fieldPrefix}-card`) as HTMLElement;
        if (!itemCard) return;
        
        // Show the ingredient form again
        const itemForm = itemCard.querySelector(`.${this.config.fieldPrefix}-form`) as HTMLElement;
        if (itemForm && itemForm.hidden) {
            itemForm.hidden = false;
        }
        
        // Hide the undo section
        const hiddenUndo = itemCard.querySelector('.hidden-undo') as HTMLElement;
        if (hiddenUndo) {
            hiddenUndo.style.display = 'none';
        }
        
        // Uncheck the DELETE checkbox
        const deleteInput = itemCard.querySelector('input[name*="-DELETE"]') as HTMLInputElement;
        if (deleteInput && deleteInput.checked) {
            deleteInput.checked = false;
        }
    }

    

    hasMeaningfulChanges(currentFormData: FormData, originalFormData: FormData): boolean {
        const currentIngredients = this.extractNonEmptyIngredients(currentFormData);
        const originalIngredients = this.extractNonEmptyIngredients(originalFormData);

        return JSON.stringify(currentIngredients) !== JSON.stringify(originalIngredients);
    }

    private extractNonEmptyIngredients(formData: FormData): Array<{name: string, quantity: string, measurement: string}> {
        const ingredients: Array<{name: string, quantity: string, measurement: string}> = [];
        
        // Get all ingredient indices
        const indices = new Set<string>();
        for (const [key] of formData.entries()) {
            const match = key.match(/ingredients-(\d+)-/);
            if (match) {
                indices.add(match[1]);
            }
        }
        
        indices.forEach(index => {
            const name = formData.get(`ingredients-${index}-name`) as string;
            // Only include ingredients with a name (non-empty)
            if (name && name.trim() !== '') {
                const quantity = formData.get(`ingredients-${index}-quantity`) as string;
                const measurement = formData.get(`ingredients-${index}-measurement`) as string;
                ingredients.push({
                    name: name.trim(),
                    quantity: quantity || '',
                    measurement: measurement || ''
                });
            }
        });
        
        return ingredients;
    }

    protected removeItemForm(button: HTMLElement): void {
        const itemCard = button.closest('.ingredient-card') as HTMLElement;
        if (!itemCard) return;
        let itemForm = itemCard.querySelector('.ingredient-form') as HTMLElement;
        if (!itemForm) return;

        itemForm.hidden = true;
        const undoButton = itemCard.querySelector('.hidden-undo') as HTMLElement;
        if (undoButton) {
            // Show the undo button
            undoButton.style.display = 'block';
        }
        // Find the hidden DELETE checkbox
        const deleteInput = itemForm.querySelector('input[name*="-DELETE"]') as HTMLInputElement;
        if (deleteInput) {
            // Mark for deletion and hide the form
            deleteInput.value = 'on';
        }
    }

    async handleUpdateSave(apiUrl: string): Promise<void>{
        super.showLoadingState()
        const csrfToken = super.getCSRFToken();
        if (!csrfToken) {
            const errorMessage = 'Cannot save ingredients: CSRF token not found.';
            super.showMessage(errorMessage);
            super.hideLoadingState();
            return;
        }
        const ingredients = this.collectFormData();

        try{
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                body: ingredients
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}, ${response.statusText}, ${response.json()}`);
            }

            const result = await response.json();
            if (result.success) {
                if(this.detailPage){
                    this.updateIngredients(result.ingredients, this.detailPage);
                }
                this.showMessage('Ingredients saved successfully.');

                
            } else {
                const errorMessage = result.error || 'Failed to save ingredients.';
                this.showMessage(errorMessage);
            }
        }
        catch(error){
            const errorMessage = `Error saving ingredients: ${error instanceof Error ? error.message : 'Unknown error'}`;
            this.showMessage(errorMessage);
        }
        this.reloadItems = true; // indicating to fetch data again on modal open
        super.hideLoadingState();
    }

    private updateIngredients(ingredients: Ingredient[], detailsPage: HTMLElement): void {
        const ingredientsList = detailsPage.querySelector('#ingredients-detail-list ul');
        if(!ingredientsList) return;

        ingredientsList.innerHTML = '';
        const activeIngredients = ingredients.filter(ingredients => !ingredients.isDeleted);

        activeIngredients.forEach(ingredient => {
            const li = document.createElement('li');
            const quantity = ingredient.quantity ? `${ingredient.quantity}` : '';
            const measurement = ingredient.measurement ? `${ingredient.measurement}` : '';
            li.textContent = `${quantity} ${measurement} ${ingredient.name}`

            // Hidden input to store ingredient ID for potential future use
            const deleteInput = document.createElement('input');
            deleteInput.type = 'hidden';
            deleteInput.name = `ingredients-${ingredient.id}-DELETE`;
            deleteInput.value = 'false';
            li.appendChild(deleteInput);
            ingredientsList.appendChild(li);
            
        })
    }

    handleCreateSave(): void {
        // For create mode: saving to hidden form fields
        console.log('Handling create save - saving to hidden form');
        
        const saveIngredietsCount = this.saveIngredientsToHiddenForm();
        const message = `${saveIngredietsCount} ingredients saved to recipe form.`;
        this.showMessage(message);
    }

    private saveIngredientsToHiddenForm(): number| null {
        const mainForm = document.getElementById(`${this.config.mainFormId}`) as HTMLElement;
        if (!mainForm) {
            console.error('Main recipe form not found');
            return null;
        }

        // Get the ingredients hidden container
        const ingredientsContainer = mainForm.querySelector('#ingredients-hidden') as HTMLElement;
        if (!ingredientsContainer) {
            console.error('Ingredients hidden container not found');
            return null;
        }

        // Clear existing hidden inputs
        ingredientsContainer.innerHTML = '';

        // Collect ingredient data from modal
        const ingredientCards = this.htmlModal.querySelectorAll('.ingredient-card');
        let ingredientIndex = 0;

        ingredientCards.forEach(card => {
            const ingredientForm = card.querySelector('.ingredient-form') as HTMLElement;
            if (ingredientForm && !ingredientForm.hidden) {
                const nameInput = ingredientForm.querySelector('input[name*="name"]') as HTMLInputElement;
                const quantityInput = ingredientForm.querySelector('input[name*="quantity"]') as HTMLInputElement;
                const measurementInput = ingredientForm.querySelector('select[name*="measurement"]') as HTMLSelectElement;

                if (nameInput?.value) {
                    // Create hidden inputs for each ingredient field
                    super.createHiddenInput(ingredientsContainer, `ingredients-${ingredientIndex}-name`, nameInput.value, 'hidden');
                    super.createHiddenInput(ingredientsContainer, `ingredients-${ingredientIndex}-quantity`, quantityInput.value || '', 'hidden');
                    super.createHiddenInput(ingredientsContainer, `ingredients-${ingredientIndex}-measurement`, measurementInput?.value || '', 'hidden');
                    super.createHiddenInput(ingredientsContainer, `ingredients-${ingredientIndex}-DELETE`, 'false', 'hidden');
                    
                    ingredientIndex++;
                }
            }
        });

        // Add management form hidden inputs
        super.createHiddenInput(ingredientsContainer, 'ingredients-TOTAL_FORMS', ingredientIndex.toString(), 'hidden');
        super.createHiddenInput(ingredientsContainer, 'ingredients-INITIAL_FORMS', '0', 'hidden');
        super.createHiddenInput(ingredientsContainer, 'ingredients-MIN_NUM_FORMS', '0', 'hidden');
        super.createHiddenInput(ingredientsContainer, 'ingredients-MAX_NUM_FORMS', '1000', 'hidden');

        return ingredientIndex;
    }
    // Ingredients formset management
    addItemToForm(): void {

        let formsetDiv = this.htmlModal.querySelector<HTMLElement>('#ingredients-formset');
        let totalFormsInput = this.htmlModal.querySelector<HTMLInputElement>('#id_ingredients-TOTAL_FORMS');

        if (!formsetDiv || !totalFormsInput) {
            console.error('Formset div or TOTAL_FORMS input not found.');
            return;
        }
        
        let totalForms = parseInt(totalFormsInput.value, 10);

        const existingForm = formsetDiv.querySelector<HTMLElement>('.ingredient-form');
        if (!existingForm) {
            console.error('No existing form found to use as template.');
            return;
        }
        
        const existingCard = existingForm.closest('.ingredient-card') as HTMLElement;
        if (!existingCard) {
            console.error('No existing card found to use as template.');
            return;
        }
        
        const newCard = existingCard.cloneNode(true) as HTMLElement;
        const ingredientForm = newCard.querySelector('.ingredient-form') as HTMLElement;
        if (ingredientForm.hidden) {
            ingredientForm.hidden = false;
        }
        
        // Clear the form values
        const inputs = newCard.querySelectorAll('input, select, textarea');
        inputs.forEach((input: Element) => {
            if (input instanceof HTMLInputElement || input instanceof HTMLSelectElement || input instanceof HTMLTextAreaElement) {
                input.value = '';
            }
        });
        
        // Update the form indices
        const formIndex = totalForms;
        inputs.forEach((input: Element) => {
            if (input instanceof HTMLInputElement || input instanceof HTMLSelectElement || input instanceof HTMLTextAreaElement) {
                const name = input.name;
                if (name) {
                    input.name = name.replace(/ingredients-\d+/, `ingredients-${formIndex}`);
                }
                const id = input.id;
                if (id) {
                    input.id = id.replace(/id_ingredients-\d+/, `id_ingredients-${formIndex}`);
                }
            }
        });

        // Hide the undo section for new cards
        const hiddenUndo = newCard.querySelector('.hidden-undo') as HTMLElement;
        if (hiddenUndo) {
            hiddenUndo.style.display = 'none';
        }
        // Create hidden DELETE checkbox for the new form
        const hiddenDeleteDiv = document.createElement('div');
        hiddenDeleteDiv.className = 'hidden-delete';
        hiddenDeleteDiv.style.display = 'none';
        hiddenDeleteDiv.innerHTML = `
            <input type="checkbox" name="ingredients-${formIndex}-DELETE" id="id_ingredients-${formIndex}-DELETE">`;

        formsetDiv.appendChild(newCard);
        formsetDiv.appendChild(hiddenDeleteDiv);
        totalFormsInput.value = (totalForms + 1).toString();
    }
}