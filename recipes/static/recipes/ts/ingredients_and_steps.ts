

export class IngredientsAndStepsManager {
    private addStepButton: HTMLButtonElement;

    constructor() {
        this.addStepButton = document.getElementById('add-step-button') as HTMLButtonElement;
        this.setUpListeners();
    }


    private setUpListeners(): void {
        if (this.addStepButton) {
            this.addStepButton.addEventListener('click', (event) => {
                event.preventDefault();
                this.addStepForm();
            });
        }
    }
        
    
    private addStepForm(): void {
        if (!this.addStepButton) {
            console.error('Main form is not initialized.');
            return;
        }
        const mainForm = this.addStepButton;
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