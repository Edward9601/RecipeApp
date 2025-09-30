export class IngredientsAndStepsManager {
    constructor() {
        this.addStepButton = document.getElementById('add-step-button');
        this.setUpListeners();
    }
    setUpListeners() {
        if (this.addStepButton) {
            this.addStepButton.addEventListener('click', (event) => {
                event.preventDefault();
                this.addStepForm();
            });
        }
    }
    addStepForm() {
        if (!this.addStepButton) {
            console.error('Main form is not initialized.');
            return;
        }
        const mainForm = this.addStepButton;
        let formsetDiv = mainForm.querySelector('#step-formset');
        let totalFormsInput = mainForm.querySelector('#id_steps-TOTAL_FORMS');
        if (!formsetDiv || !totalFormsInput) {
            console.error('Formset div or TOTAL_FORMS input not found.');
            return;
        }
        let totalForms = parseInt(totalFormsInput.value, 10);
        // Get the empty form template and clone it
        let emptyFormTemplate = mainForm.querySelector('#empty-step-form');
        if (!emptyFormTemplate) {
            console.error('Empty form template not found.');
            return;
        }
        const newForm = emptyFormTemplate.cloneNode(true);
        newForm.classList.add('step-form');
        newForm.removeAttribute('id');
        newForm.style.removeProperty('display');
        const updatedHTML = newForm.innerHTML.replace(/__prefix__/g, totalForms.toString());
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = updatedHTML;
        const orderInput = tempDiv.querySelector('input[name$="-order"]');
        if (orderInput) {
            orderInput.value = (totalForms + 1).toString();
        }
        newForm.innerHTML = tempDiv.innerHTML;
        formsetDiv.appendChild(newForm);
        totalFormsInput.value = (totalForms + 1).toString();
    }
}
//# sourceMappingURL=ingredients_and_steps.js.map