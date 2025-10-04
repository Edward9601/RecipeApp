var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { BaseFormManager } from "./base_recipe_item.js";
export class IngredientsManager extends BaseFormManager {
    constructor(config) {
        super(config);
        this.SetUpActionButtonsModalEventListener();
    }
    SetUpActionButtonsModalEventListener() {
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
                    const apiUrl = this.saveButton.dataset.url;
                    this.handleUpdateSave(apiUrl);
                    this.closeModal(this.htmlModal);
                }
                else {
                    this.handleCreateSave();
                    this.closeModal(this.htmlModal);
                }
            });
        }
    }
    setUpButtonsDelegationEventListeners() {
        const itemList = this.htmlModal.querySelector('#ingredients-list');
        if (itemList) {
            itemList.addEventListener('click', (event) => {
                const target = event.target;
                if (target.matches('.remove-button')) {
                    event.preventDefault();
                    this.removeItemForm(target);
                }
                if (target.matches('.undo-btn')) {
                    event.preventDefault();
                    this.undoRemoveItemForm(target);
                }
            });
        }
        else {
            console.error(`${this.config.fieldPrefix}s list not found.`);
        }
    }
    undoRemoveItemForm(button) {
        const itemCard = button.closest(`.${this.config.fieldPrefix}-card`);
        if (!itemCard)
            return;
        // Show the ingredient form again
        const itemForm = itemCard.querySelector(`.${this.config.fieldPrefix}-form`);
        if (itemForm && itemForm.hidden) {
            itemForm.hidden = false;
        }
        // Hide the undo section
        const hiddenUndo = itemCard.querySelector('.hidden-undo');
        if (hiddenUndo) {
            hiddenUndo.style.display = 'none';
        }
        // Uncheck the DELETE checkbox
        const deleteInput = itemCard.querySelector('input[name*="-DELETE"]');
        if (deleteInput && deleteInput.checked) {
            deleteInput.checked = false;
        }
    }
    hasMeaningfulChanges(currentFormData, originalFormData) {
        const currentIngredients = this.extractNonEmptyIngredients(currentFormData);
        const originalIngredients = this.extractNonEmptyIngredients(originalFormData);
        return JSON.stringify(currentIngredients) !== JSON.stringify(originalIngredients);
    }
    extractNonEmptyIngredients(formData) {
        const ingredients = [];
        // Get all ingredient indices
        const indices = new Set();
        for (const [key] of formData.entries()) {
            const match = key.match(/ingredients-(\d+)-/);
            if (match) {
                indices.add(match[1]);
            }
        }
        indices.forEach(index => {
            const name = formData.get(`ingredients-${index}-name`);
            // Only include ingredients with a name (non-empty)
            if (name && name.trim() !== '') {
                const quantity = formData.get(`ingredients-${index}-quantity`);
                const measurement = formData.get(`ingredients-${index}-measurement`);
                ingredients.push({
                    name: name.trim(),
                    quantity: quantity || '',
                    measurement: measurement || ''
                });
            }
        });
        return ingredients;
    }
    removeItemForm(button) {
        const itemCard = button.closest('.ingredient-card');
        if (!itemCard)
            return;
        let itemForm = itemCard.querySelector('.ingredient-form');
        if (!itemForm)
            return;
        itemForm.hidden = true;
        const undoButton = itemCard.querySelector('.hidden-undo');
        if (undoButton) {
            // Show the undo button
            undoButton.style.display = 'block';
        }
        // Find the hidden DELETE checkbox
        const deleteInput = itemForm.querySelector('input[name*="-DELETE"]');
        if (deleteInput) {
            // Mark for deletion and hide the form
            deleteInput.value = 'on';
        }
    }
    handleUpdateSave(apiUrl) {
        const _super = Object.create(null, {
            showLoadingState: { get: () => super.showLoadingState },
            getCSRFToken: { get: () => super.getCSRFToken },
            showMessage: { get: () => super.showMessage },
            hideLoadingState: { get: () => super.hideLoadingState }
        });
        return __awaiter(this, void 0, void 0, function* () {
            _super.showLoadingState.call(this);
            const csrfToken = _super.getCSRFToken.call(this);
            if (!csrfToken) {
                const errorMessage = 'Cannot save ingredients: CSRF token not found.';
                _super.showMessage.call(this, errorMessage);
                _super.hideLoadingState.call(this);
                return;
            }
            const ingredients = this.collectFormData();
            try {
                const response = yield fetch(apiUrl, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken
                    },
                    body: ingredients
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}, ${response.statusText}, ${response.json()}`);
                }
                const result = yield response.json();
                if (result.success) {
                    if (this.detailPage) {
                        this.updateIngredients(result.ingredients, this.detailPage);
                    }
                    this.showMessage('Ingredients saved successfully.');
                }
                else {
                    const errorMessage = result.error || 'Failed to save ingredients.';
                    this.showMessage(errorMessage);
                }
            }
            catch (error) {
                const errorMessage = `Error saving ingredients: ${error instanceof Error ? error.message : 'Unknown error'}`;
                this.showMessage(errorMessage);
            }
            this.reloadItems = true; // indicating to fetch data again on modal open
            _super.hideLoadingState.call(this);
        });
    }
    updateIngredients(ingredients, detailsPage) {
        const ingredientsList = detailsPage.querySelector('#ingredients-detail-list ul');
        if (!ingredientsList)
            return;
        ingredientsList.innerHTML = '';
        const activeIngredients = ingredients.filter(ingredients => !ingredients.isDeleted);
        activeIngredients.forEach(ingredient => {
            const li = document.createElement('li');
            const quantity = ingredient.quantity ? `${ingredient.quantity}` : '';
            const measurement = ingredient.measurement ? `${ingredient.measurement}` : '';
            li.textContent = `${quantity} ${measurement} ${ingredient.name}`;
            // Hidden input to store ingredient ID for potential future use
            const deleteInput = document.createElement('input');
            deleteInput.type = 'hidden';
            deleteInput.name = `ingredients-${ingredient.id}-DELETE`;
            deleteInput.value = 'false';
            li.appendChild(deleteInput);
            ingredientsList.appendChild(li);
        });
    }
    handleCreateSave() {
        // For create mode: saving to hidden form fields
        console.log('Handling create save - saving to hidden form');
        const saveIngredietsCount = this.saveIngredientsToHiddenForm();
        const message = `${saveIngredietsCount} ingredients saved to recipe form.`;
        this.showMessage(message);
    }
    saveIngredientsToHiddenForm() {
        const mainForm = document.getElementById(`${this.config.mainFormId}`);
        if (!mainForm) {
            console.error('Main recipe form not found');
            return null;
        }
        // Get the ingredients hidden container
        const ingredientsContainer = mainForm.querySelector('#ingredients-hidden');
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
            const ingredientForm = card.querySelector('.ingredient-form');
            if (ingredientForm && !ingredientForm.hidden) {
                const nameInput = ingredientForm.querySelector('input[name*="name"]');
                const quantityInput = ingredientForm.querySelector('input[name*="quantity"]');
                const measurementInput = ingredientForm.querySelector('select[name*="measurement"]');
                if (nameInput === null || nameInput === void 0 ? void 0 : nameInput.value) {
                    // Create hidden inputs for each ingredient field
                    super.createHiddenInput(ingredientsContainer, `ingredients-${ingredientIndex}-name`, nameInput.value, 'hidden');
                    super.createHiddenInput(ingredientsContainer, `ingredients-${ingredientIndex}-quantity`, quantityInput.value || '', 'hidden');
                    super.createHiddenInput(ingredientsContainer, `ingredients-${ingredientIndex}-measurement`, (measurementInput === null || measurementInput === void 0 ? void 0 : measurementInput.value) || '', 'hidden');
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
    addItemToForm() {
        let formsetDiv = this.htmlModal.querySelector('#ingredients-formset');
        let totalFormsInput = this.htmlModal.querySelector('#id_ingredients-TOTAL_FORMS');
        let emptyForm = this.htmlForm.querySelector('#empty-form');
        if (!formsetDiv || !totalFormsInput || !emptyForm) {
            console.error('Required elements not found.');
            return;
        }
        let totalForms = parseInt(totalFormsInput.value, 10);
        const newForm = emptyForm.cloneNode(true);
        newForm.style.display = 'block';
        const formElements = newForm.querySelectorAll('input, select, label');
        formElements.forEach((element) => {
            if (element instanceof HTMLInputElement || element instanceof HTMLSelectElement) {
                // Update names and IDs
                if (element.name) {
                    element.name = element.name.replace(/__prefix__/g, totalForms.toString());
                }
                if (element.id) {
                    element.id = element.id.replace(/__prefix__/g, totalForms.toString());
                }
            }
            // Update label's 'for' attribute
            if (element instanceof HTMLLabelElement && element.htmlFor) {
                element.htmlFor = element.htmlFor.replace(/__prefix__/g, totalForms.toString());
            }
        });
        // Hide the undo section for new cards
        const hiddenUndo = newForm.querySelector('.hidden-undo');
        if (hiddenUndo) {
            hiddenUndo.style.display = 'none';
        }
        formsetDiv.appendChild(newForm);
        totalFormsInput.value = (totalForms + 1).toString();
    }
}
//# sourceMappingURL=ingredients.js.map