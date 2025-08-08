export class IngredientsManager {
    constructor() {
        this.ingredientModal = document.getElementById('ingredientsModal');
        this.addIngredientButton = document.getElementById('add-ingredient-button');
        this.SetUpIngredientsModalEventListener();
    }
    SetUpIngredientsModalEventListener() {
        if (this.addIngredientButton) {
            this.addIngredientButton.addEventListener('click', (event) => {
                event.preventDefault();
                this.addIngredientForm();
            });
        }
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
        // Set up event delegation for remove buttons
        this.setUpButtonsDelegationEventListeners();
    }
    setUpButtonsDelegationEventListeners() {
        const ingredientsList = this.ingredientModal.querySelector('#ingredients-list');
        if (ingredientsList) {
            ingredientsList.addEventListener('click', (event) => {
                const target = event.target;
                if (target.matches('.remove-button')) {
                    event.preventDefault();
                    this.removeIngredientForm(target);
                }
                if (target.matches('.undo-btn')) {
                    event.preventDefault();
                    this.undoRemoveIngredientForm(target);
                }
            });
        }
        else {
            console.error('Ingredients list not found.');
        }
    }
    undoRemoveIngredientForm(button) {
        const ingredientCard = button.closest('.ingredient-card');
        if (!ingredientCard)
            return;
        // Show the ingredient form again
        const ingredientForm = ingredientCard.querySelector('.ingredient-form');
        if (ingredientForm && ingredientForm.hidden) {
            ingredientForm.hidden = false;
        }
        // Hide the undo section
        const hiddenUndo = ingredientCard.querySelector('.hidden-undo');
        if (hiddenUndo) {
            hiddenUndo.style.display = 'none';
        }
        // Uncheck the DELETE checkbox
        const deleteCheckbox = ingredientCard.querySelector('input[type="checkbox"]');
        if (deleteCheckbox && deleteCheckbox.checked) {
            deleteCheckbox.checked = false;
        }
    }
    removeIngredientForm(button) {
        const ingredientCardContent = button.closest('.ingredient-card');
        if (!ingredientCardContent)
            return;
        let ingredientForm = ingredientCardContent.querySelector('.ingredient-form');
        if (!ingredientForm)
            return;
        ingredientForm.hidden = true;
        const undoButton = ingredientCardContent.querySelector('.hidden-undo');
        if (undoButton) {
            // Show the undo button
            undoButton.style.display = 'block';
        }
        // Find the hidden DELETE checkbox
        const deleteCheckbox = ingredientCardContent.querySelector('input[type="checkbox"]');
        if (deleteCheckbox) {
            // Mark for deletion and hide the form
            deleteCheckbox.checked = true;
        }
    }
    // Ingredients and Steps formset management
    addIngredientForm() {
        let formsetDiv = this.ingredientModal.querySelector('#ingredient-formset');
        let totalFormsInput = this.ingredientModal.querySelector('#id_ingredients-TOTAL_FORMS');
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
        // Clone the entire ingredient card (not just the form)
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
        const inputsToUpdate = newCard.querySelectorAll('input, select, textarea');
        inputsToUpdate.forEach((input) => {
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
            <input type="checkbox" name="ingredients-${formIndex}-DELETE" id="id_ingredients-${formIndex}-DELETE">
        `;
        formsetDiv.appendChild(newCard);
        formsetDiv.appendChild(hiddenDeleteDiv);
        totalFormsInput.value = (totalForms + 1).toString();
    }
}
//# sourceMappingURL=ingredients.js.map