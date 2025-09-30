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
        var _a, _b;
        super(config);
        this.reloadIngredients = false;
        this.isUpdateMode = ((_b = (_a = this.saveButton) === null || _a === void 0 ? void 0 : _a.getAttribute('data-mode')) === null || _b === void 0 ? void 0 : _b.match(/update/i)) ? true : false;
        this.SetUpModalEventListener();
        this.setUpModalCloseProtection(this.htmlModal, this.htmlForm);
    }
    SetUpModalEventListener() {
        document.body.addEventListener('htmx:afterSwap', (event) => {
            // Cast to CustomEvent with detail property
            const customEvent = event;
            if (customEvent.detail && customEvent.detail.target.id === 'ingredients-modal-container') {
                const modalEl = document.getElementById('ingredientsModal');
                if (modalEl) {
                    const modal = new window.bootstrap.Modal(modalEl);
                    modal.show();
                }
            }
        });
        super.SetUpModalEventListener();
        // Set up event delegation for remove buttons
        super.setUpButtonsDelegationEventListeners('#ingredients-list');
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
    setUpModalCloseProtection(ingredientModal, ingredientsForm) {
        const _super = Object.create(null, {
            checkForChanges: { get: () => super.checkForChanges },
            closeModal: { get: () => super.closeModal }
        });
        return __awaiter(this, void 0, void 0, function* () {
            ingredientModal.addEventListener('hide.bs.modal', (event) => {
                _super.checkForChanges.call(this, ingredientsForm);
                if (this.hasUnsavedChanges) {
                    event.preventDefault();
                    this.unsavedChangesManager.show(() => __awaiter(this, void 0, void 0, function* () {
                        const apiUrl = this.saveButton.dataset.url;
                        this.hasUnsavedChanges = false;
                        yield this.handleUpdateSave(apiUrl);
                        _super.closeModal.call(this, this.htmlModal);
                    }), () => {
                        this.reloadItems = true; // indicating to fetch data again on modal open
                        this.hasUnsavedChanges = false;
                        _super.closeModal.call(this, this.htmlModal);
                    });
                }
            });
        });
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
            this.reloadIngredients = true; // indicating to fetch data again on modal open
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
            li.textContent = `${ingredient.name} ${quantity} ${measurement}`;
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
                    super.createHiddenInput(ingredientsContainer, `ingredients-${ingredientIndex}-name`, nameInput.value);
                    super.createHiddenInput(ingredientsContainer, `ingredients-${ingredientIndex}-quantity`, quantityInput.value || '');
                    super.createHiddenInput(ingredientsContainer, `ingredients-${ingredientIndex}-measurement`, (measurementInput === null || measurementInput === void 0 ? void 0 : measurementInput.value) || '');
                    super.createHiddenInput(ingredientsContainer, `ingredients-${ingredientIndex}-DELETE`, 'false');
                    ingredientIndex++;
                }
            }
        });
        // Add management form hidden inputs
        super.createHiddenInput(ingredientsContainer, 'ingredients-TOTAL_FORMS', ingredientIndex.toString());
        super.createHiddenInput(ingredientsContainer, 'ingredients-INITIAL_FORMS', '0');
        super.createHiddenInput(ingredientsContainer, 'ingredients-MIN_NUM_FORMS', '0');
        super.createHiddenInput(ingredientsContainer, 'ingredients-MAX_NUM_FORMS', '1000');
        return ingredientIndex;
    }
    // Ingredients formset management
    addItemToForm() {
        let formsetDiv = this.htmlModal.querySelector('#ingredients-formset');
        let totalFormsInput = this.htmlModal.querySelector('#id_ingredients-TOTAL_FORMS');
        if (!formsetDiv || !totalFormsInput) {
            console.error('Formset div or TOTAL_FORMS input not found.');
            return;
        }
        let totalForms = parseInt(totalFormsInput.value, 10);
        const existingForm = formsetDiv.querySelector('.ingredient-form');
        if (!existingForm) {
            console.error('No existing form found to use as template.');
            return;
        }
        const existingCard = existingForm.closest('.ingredient-card');
        if (!existingCard) {
            console.error('No existing card found to use as template.');
            return;
        }
        const newCard = existingCard.cloneNode(true);
        const ingredientForm = newCard.querySelector('.ingredient-form');
        if (ingredientForm.hidden) {
            ingredientForm.hidden = false;
        }
        // Clear the form values
        const inputs = newCard.querySelectorAll('input, select, textarea');
        inputs.forEach((input) => {
            if (input instanceof HTMLInputElement || input instanceof HTMLSelectElement || input instanceof HTMLTextAreaElement) {
                input.value = '';
            }
        });
        // Update the form indices
        const formIndex = totalForms;
        inputs.forEach((input) => {
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
        const hiddenUndo = newCard.querySelector('.hidden-undo');
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
//# sourceMappingURL=ingredients.js.map