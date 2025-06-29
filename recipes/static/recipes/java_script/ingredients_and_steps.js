export class IngredientsAndStepsManager {
    constructor(form) {
        this.form = form;
        this.addIngredientButton = document.getElementById('addIngredientButton');
        this.addStepButton = document.getElementById('add-step-button');
        this.setUpListeners();
    }
    setUpListeners() {
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
    addIngredientForm() {
        if (!this.form) {
            console.error('Main form is not initialized.');
            return;
        }
        let formsetDiv = this.form.querySelector('#ingredient-formset');
        let totalFormsInput = this.form.querySelector('#id_ingredients-TOTAL_FORMS');
        if (!formsetDiv || !totalFormsInput) {
            console.error('Formset div or TOTAL_FORMS input not found.');
            return;
        }
        // Get the current total number of forms
        let totalForms = parseInt(totalFormsInput.value, 10);
        // Get the empty form template, then clone the empty form
        let emptyFormTemplate = this.form.querySelector('#empty-ingredient-form');
        if (!emptyFormTemplate) {
            console.error('Empty form template not found.');
            return;
        }
        const newForm = emptyFormTemplate.cloneNode(true);
        newForm.classList.add('ingredient-form');
        newForm.removeAttribute('id');
        newForm.style.removeProperty('display');
        newForm.innerHTML = newForm.innerHTML.replace(/__prefix__/g, totalForms.toString());
        formsetDiv.appendChild(newForm);
        totalFormsInput.value = (totalForms + 1).toString();
    }
    addStepForm() {
        if (!this.form) {
            console.error('Main form is not initialized.');
            return;
        }
        const mainForm = this.form;
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