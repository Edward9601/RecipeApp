export class IngredientsAndStepsManager {
    private form: HTMLElement;
    private addIngredientButton: HTMLButtonElement;
    private addStepButton: HTMLButtonElement;

    constructor(form: HTMLElement) {
        this.form = form;
        this.addIngredientButton = document.getElementById('addIngredientButton') as HTMLButtonElement;
        this.addStepButton = document.getElementById('add-step-button') as HTMLButtonElement;

        this.setUpListeners();
    }


    private setUpListeners(): void {
        if (this.addIngredientButton) {
            this.addIngredientButton.addEventListener('click', (event) => {
                event.preventDefault();
                this.addIngredientForm();
            });
        }

        if (this.addStepButton) {
            this.addStepButton.addEventListener('click', (event) => {
                event.preventDefault();
                this.addStepForm();
            });
        }
    }


    // Ingredients and Steps formset management
    private addIngredientForm(): void {
        if(!this.form){
            console.error('Main form is not initialized.')
            return;
        }

        let formsetDiv = this.form.querySelector<HTMLElement>('#ingredient-formset');

        let totalFormsInput = this.form.querySelector<HTMLInputElement>('#id_ingredients-TOTAL_FORMS');

        if (!formsetDiv || !totalFormsInput) {
            console.error('Formset div or TOTAL_FORMS input not found.');
            return;
        }
        // Get the current total number of forms
        let totalForms = parseInt(totalFormsInput.value, 10);

        // Get the empty form template, then clone the empty form
        let emptyFormTemplate = this.form.querySelector<HTMLElement>('#empty-ingredient-form');
        if (!emptyFormTemplate) {
            console.error('Empty form template not found.');
            return;
        }
        const newForm = emptyFormTemplate.cloneNode(true) as HTMLElement;
        newForm.classList.add('ingredient-form');
        newForm.removeAttribute('id');
        newForm.style.removeProperty('display');
        newForm.innerHTML = newForm.innerHTML.replace(/__prefix__/g, totalForms.toString());

        formsetDiv.appendChild(newForm);

        totalFormsInput.value = (totalForms + 1).toString();
    }
    
    private addStepForm(): void {
        if (!this.form) {
            console.error('Main form is not initialized.');
            return;
        }
        const mainForm = this.form;
        let formsetDiv = mainForm.querySelector<HTMLElement>('#step-formset');
        let totalFormsInput = mainForm.querySelector<HTMLInputElement>('#id_steps-TOTAL_FORMS');
        if (!formsetDiv || !totalFormsInput) {
            console.error('Formset div or TOTAL_FORMS input not found.');
            return;
        }
        let totalForms = parseInt(totalFormsInput.value, 10);

        // Get the empty form template and clone it
        let emptyFormTemplate = mainForm.querySelector<HTMLElement>('#empty-step-form');
        if (!emptyFormTemplate) {
            console.error('Empty form template not found.');
            return;
        }
        const newForm = emptyFormTemplate.cloneNode(true) as HTMLElement;
        newForm.classList.add('step-form');
        newForm.removeAttribute('id');
        newForm.style.removeProperty('display');

        const updatedHTML = newForm.innerHTML.replace(/__prefix__/g, totalForms.toString());

        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = updatedHTML;

        const orderInput = tempDiv.querySelector<HTMLInputElement>('input[name$="-order"]');
        if (orderInput) {
            orderInput.value = (totalForms + 1).toString();
        }

        newForm.innerHTML = tempDiv.innerHTML;
        formsetDiv.appendChild(newForm);

        totalFormsInput.value = (totalForms + 1).toString();
    }
}