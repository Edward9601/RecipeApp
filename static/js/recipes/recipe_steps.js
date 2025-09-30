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
export class StepsManager extends BaseFormManager {
    constructor(config) {
        var _a;
        super(config);
        this.reloadSteps = false;
        this.isUpdateMode = ((_a = this.saveButton.getAttribute('data-mode')) === null || _a === void 0 ? void 0 : _a.match(/update/i)) ? true : false;
        this.SetUpModalEventListener();
        this.setUpModalCloseProtection(this.htmlModal, this.htmlForm);
    }
    SetUpModalEventListener() {
        document.body.addEventListener('htmx:afterSwap', (event) => {
            // Cast to CustomEvent with detail property
            const customEvent = event;
            if (customEvent.detail && customEvent.detail.target.id === 'steps-modal-container') {
                const modalEl = document.getElementById('stepsModal');
                if (modalEl) {
                    const modal = new window.bootstrap.Modal(modalEl);
                    modal.show();
                    this.originalFormData = this.getFormData(this.htmlForm);
                }
            }
        });
        super.SetUpModalEventListener();
        // Set up event delegation for remove buttons
        super.setUpButtonsDelegationEventListeners('#steps-list');
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
            collectFormData: { get: () => super.collectFormData }
        });
        return __awaiter(this, void 0, void 0, function* () {
            this.showLoadingState();
            const csrfToken = this.getCSRFToken();
            if (!csrfToken) {
                const errorMessage = 'Cannot update recipe steps: CSRF token not found.';
                this.showMessage(errorMessage);
                this.hideLoadingState();
                return;
            }
            const steps = _super.collectFormData.call(this);
            try {
                const response = yield fetch(apiUrl, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken
                    },
                    body: steps
                });
                if (!response.ok) {
                    const textResponse = yield response.text();
                    console.error('Server response:', textResponse);
                    throw new Error(`Server error: ${response.status} ${response.statusText}`);
                }
                const result = yield response.json();
                if (result.success) {
                    this.showMessage('Steps saved successfully.');
                    if (this.detailPage) {
                        this.updateFormStep(result.steps, this.detailPage);
                    }
                }
                else {
                    const errorMessage = result.error || 'Failed to save Steps.';
                    this.showMessage(errorMessage);
                }
            }
            catch (error) {
                const errorMessage = `Error saving steps: ${error instanceof Error ? error.message : 'Unknown error'}`;
                this.showMessage(errorMessage);
            }
            this.reloadSteps = true; // indicating to fetch data again on modal open
            this.hideLoadingState();
        });
    }
    updateFormStep(steps, detailsPage) {
        // Clear existing steps
        const stepsContainer = detailsPage.querySelector('#steps-detail-list ol');
        if (!stepsContainer) {
            console.error('Steps container not found in the detail page.');
            return;
        }
        stepsContainer.innerHTML = '';
        const sortedSteps = [...steps].sort((a, b) => a.order - b.order);
        // Populate with updated steps
        sortedSteps.forEach((step) => {
            const li = document.createElement('li');
            li.textContent = step.description;
            const orderInput = document.createElement('input');
            orderInput.type = 'hidden';
            orderInput.value = step.order.toString();
            li.appendChild(orderInput);
            const deleteInput = document.createElement('input');
            deleteInput.type = 'hidden';
            deleteInput.value = step.isDeleted ? 'on' : '';
            li.appendChild(deleteInput);
            stepsContainer.appendChild(li);
        });
    }
    addItemToForm() {
        const mainForm = this.htmlModal;
        let formsetDiv = mainForm.querySelector('#steps-formset');
        let totalFormsInput = mainForm.querySelector('#id_steps-TOTAL_FORMS');
        if (!formsetDiv || !totalFormsInput) {
            console.error('Formset div or TOTAL_FORMS input not found.');
            return;
        }
        let totalForms = parseInt(totalFormsInput.value, 10);
        const stepsForm = mainForm.querySelector('.step-form');
        if (!stepsForm) {
            console.error('Empty form template not found.');
            return;
        }
        const stepsCard = mainForm.querySelector('.step-card');
        if (!stepsCard) {
            console.error('Steps card not found.');
            return;
        }
        const newStepsCard = stepsCard.cloneNode(true);
        const newStepsFrom = newStepsCard.querySelector('.step-form');
        if (!newStepsFrom) {
            console.error('Cloned form not found.');
            return;
        }
        const inputs = newStepsCard.querySelectorAll('input, textarea, select, label');
        inputs.forEach((element) => {
            if (element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement || element instanceof HTMLSelectElement) {
                element.value = '';
            }
        });
        const formIndex = totalForms;
        inputs.forEach((element) => {
            if (element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement || element instanceof HTMLSelectElement) {
                const name = element.name;
                if (name) {
                    element.name = name.replace(/steps-(\d+)-/, `steps-${formIndex}-`);
                }
                const id = element.id;
                if (id) {
                    element.id = id.replace(/id_steps-(\d+)-/, `id_steps-${formIndex}-`);
                }
            }
        });
        const orderInput = newStepsCard.querySelector('input[name*="order"]');
        if (orderInput) {
            orderInput.value = (formIndex + 1).toString();
        }
        // Hide the undo section for new cards
        const hiddenUndo = newStepsCard.querySelector('.hidden-undo');
        if (hiddenUndo) {
            hiddenUndo.style.display = 'none';
        }
        // Create hidden DELETE checkbox for the new form
        const hiddenDeleteDiv = document.createElement('div');
        hiddenDeleteDiv.className = 'hidden-delete';
        hiddenDeleteDiv.style.display = 'none';
        hiddenDeleteDiv.innerHTML = `
            <input type="checkbox" name="steps-${formIndex}-DELETE" id="id_steps-${formIndex}-DELETE">`;
        formsetDiv.appendChild(newStepsCard);
        formsetDiv.appendChild(hiddenDeleteDiv);
        totalFormsInput.value = (totalForms + 1).toString();
    }
    hasMeaningfulChanges(currentFormData, originalFormData) {
        const currentSteps = this.extractNonEmptySteps(currentFormData);
        const originalSteps = this.extractNonEmptySteps(originalFormData);
        return JSON.stringify(currentSteps) !== JSON.stringify(originalSteps);
    }
    extractNonEmptySteps(formData) {
        const steps = [];
        // Get all steps indices
        const indices = new Set();
        for (const [key] of formData.entries()) {
            const match = key.match(/steps-(\d+)-/);
            if (match) {
                indices.add(match[1]);
            }
        }
        indices.forEach(index => {
            const description = formData.get(`steps-${index}-description`);
            // Only include steps with a desctiption (non-empty)
            if (description && description.trim() !== '') {
                const order = parseInt(formData.get(`steps-${index}-order`), 10) || undefined;
                const id = parseInt(formData.get(`steps-${index}-id`), 10) || undefined;
                if (order && id) {
                    const isDeleted = formData.get(`steps-${index}-DELETE`) === 'on';
                    steps.push({
                        id: id,
                        description: description.trim(),
                        order: order,
                        isDeleted: isDeleted
                    });
                }
            }
        });
        return steps;
    }
    handleCreateSave() {
    }
}
//# sourceMappingURL=recipe_steps.js.map