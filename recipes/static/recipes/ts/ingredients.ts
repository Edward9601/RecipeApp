export class IngredientsManager {
    private ingredientModal: HTMLElement;
    private addIngredientButton: HTMLButtonElement;

    constructor() {
        this.ingredientModal = document.getElementById('ingredientsModal') as HTMLElement;
        this.addIngredientButton = document.getElementById('add-ingredient-button') as HTMLButtonElement;
        this.SetUpIngredientsModalEventListener();
    }

    private SetUpIngredientsModalEventListener(){
        if (this.addIngredientButton) {
            this.addIngredientButton.addEventListener('click', (event) => {
                event.preventDefault();
                this.addIngredientForm();
            });
        }
        document.body.addEventListener('htmx:afterSwap', (event: Event) => {
            // Cast to CustomEvent with detail property
            const customEvent = event as CustomEvent<{ target: HTMLElement }>;
            if (customEvent.detail && customEvent.detail.target.id === 'ingredients-modal-container') {
                const modalEl = document.getElementById('ingredientsModal') as HTMLElement;
                if (modalEl) {
                    const modal = new (window as any).bootstrap.Modal(modalEl);
                    modal.show();
                }}
            });
    
        // Set up event delegation for remove buttons
        this.setUpButtonsDelegationEventListeners();
    }


    private setUpButtonsDelegationEventListeners(): void {
        const ingredientsList = this.ingredientModal.querySelector('#ingredients-list') as HTMLElement;
        if (ingredientsList) {
            ingredientsList.addEventListener('click', (event) => {
                const target = event.target as HTMLElement;
                if (target.matches('.remove-button')) {
                    event.preventDefault();
                    this.removeIngredientForm(target);
                }
                if(target.matches('.undo-btn')){
                    event.preventDefault();
                    this.undoRemoveIngredientForm(target);
                }
            });
        } else {
            console.error('Ingredients list not found.');
        }
    }

    private undoRemoveIngredientForm(button: HTMLElement): void {
        const ingredientCard = button.closest('.ingredient-card') as HTMLElement;
        if (!ingredientCard) return;
        
        // Show the ingredient form again
        const ingredientForm = ingredientCard.querySelector('.ingredient-form') as HTMLElement;
        if (ingredientForm && ingredientForm.hidden) {
            ingredientForm.hidden = false;
        }
        
        // Hide the undo section
        const hiddenUndo = ingredientCard.querySelector('.hidden-undo') as HTMLElement;
        if (hiddenUndo) {
            hiddenUndo.style.display = 'none';
        }
        
        // Uncheck the DELETE checkbox
        const deleteCheckbox = ingredientCard.querySelector('input[type="checkbox"]') as HTMLInputElement;
        if (deleteCheckbox && deleteCheckbox.checked) {
            deleteCheckbox.checked = false;
        }
    }
        


    private removeIngredientForm(button: HTMLElement): void {
        const ingredientCardContent = button.closest('.ingredient-card') as HTMLElement;
        if (!ingredientCardContent) return;
        let ingredientForm = ingredientCardContent.querySelector('.ingredient-form') as HTMLElement;
        if (!ingredientForm) return;

        ingredientForm.hidden = true;
        const undoButton = ingredientCardContent.querySelector('.hidden-undo') as HTMLElement;
        if (undoButton) {
            // Show the undo button
            undoButton.style.display = 'block';
        }
        // Find the hidden DELETE checkbox
        const deleteCheckbox = ingredientCardContent.querySelector('input[type="checkbox"]') as HTMLInputElement;
        if (deleteCheckbox) {
            // Mark for deletion and hide the form
            deleteCheckbox.checked = true;
        }
    }


    // Ingredients and Steps formset management
    private addIngredientForm(): void {

        let formsetDiv = this.ingredientModal.querySelector<HTMLElement>('#ingredient-formset');
        let totalFormsInput = this.ingredientModal.querySelector<HTMLInputElement>('#id_ingredients-TOTAL_FORMS');

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
        const inputsToUpdate = newCard.querySelectorAll('input, select, textarea');
        inputsToUpdate.forEach((input: Element) => {
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
            <input type="checkbox" name="ingredients-${formIndex}-DELETE" id="id_ingredients-${formIndex}-DELETE">
        `;

        formsetDiv.appendChild(newCard);
        formsetDiv.appendChild(hiddenDeleteDiv);
        totalFormsInput.value = (totalForms + 1).toString();
    }   
}