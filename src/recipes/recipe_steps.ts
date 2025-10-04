import { Step } from './interfaces/recipe_items_interfaces.js'
import { BaseFormManager } from "./base_recipe_item.js";
import { FormManagerConfig } from './interfaces/recipe_items_interfaces.js'

export class StepsManager  extends BaseFormManager<Step>{

    constructor(config: FormManagerConfig) {
        super(config)

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

    protected setUpButtonsDelegationEventListeners(): void {
        const itemList = this.htmlModal.querySelector('#steps-list') as HTMLElement;
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

    protected removeItemForm(button: HTMLElement): void {
        const itemCard = button.closest('.step-card') as HTMLElement;
        if (!itemCard) return;
        let itemForm = itemCard.querySelector('.step-form') as HTMLElement;
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

    

    private undoRemoveItemForm(button: HTMLElement): void {
        const itemCard = button.closest(`.${this.config.fieldPrefix}-card`) as HTMLElement;
        if (!itemCard) return;
        
        // Show the step form again
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


    protected async handleUpdateSave(apiUrl: string): Promise<void> {
        this.showLoadingState()
        const csrfToken = this.getCSRFToken();
        if (!csrfToken) {
            const errorMessage = 'Cannot update recipe steps: CSRF token not found.';
            this.showMessage(errorMessage);
            this.hideLoadingState();
            return;
        }
        const steps = super.collectFormData();
        try{
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                body: steps
            });

            if (!response.ok) {
                const textResponse = await response.text();
                console.error('Server response:', textResponse);
                throw new Error(`Server error: ${response.status} ${response.statusText}`);
            }

            const result = await response.json();
            if (result.success) {
                this.showMessage('Steps saved successfully.');

                if(this.detailPage){
                    this.updateFormStep(result.steps, this.detailPage)
                }
            } else {
                const errorMessage = result.error || 'Failed to save Steps.';
                this.showMessage(errorMessage);
            }
        }
        catch(error){
            const errorMessage = `Error saving steps: ${error instanceof Error ? error.message : 'Unknown error'}`;
            this.showMessage(errorMessage);
        }
        this.reloadItems = true; // indicating to fetch data again on modal open
        this.hideLoadingState();
    }

    private updateFormStep(steps: Step[], detailsPage: HTMLElement): void {
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
        
    
    addItemToForm(): void {
        const mainForm = this.htmlModal!;
        let formsetDiv = mainForm.querySelector<HTMLElement>('#steps-formset');
        let totalFormsInput = mainForm.querySelector<HTMLInputElement>('#id_steps-TOTAL_FORMS');
        let emptyForm = mainForm.querySelector<HTMLElement>('#empty-step-form');
        if (!formsetDiv || !totalFormsInput || !emptyForm) {
            console.error('Required elements not found.');
            return;
        }

        let totalForms = parseInt(totalFormsInput.value, 10);

        // Deep clone to maintain exact structure
        const newStepForm = emptyForm.cloneNode(true) as HTMLElement;
        newStepForm.style.display = 'block';

        // Update form IDs and names
        const formElements = newStepForm.querySelectorAll('input, textarea, label');
        formElements.forEach((element: Element) => {
            if (element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement) {
                // Update names and IDs
                if (element.name) {
                    element.name = element.name.replace(/__prefix__/g, totalForms.toString());
                    if(element.name.includes('order')){
                        element.value = (totalForms + 1).toString(); // Set order to current count + 1
                    }
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

        // Reset the undo section display
        const undoSection = newStepForm.querySelector('.hidden-undo');
        if (undoSection instanceof HTMLElement) {
            undoSection.style.display = 'none';
        }

        // Add to form and update total
        formsetDiv.appendChild(newStepForm);
        totalFormsInput.value = (totalForms + 1).toString();
    }


    hasMeaningfulChanges(currentFormData: FormData, originalFormData: FormData): boolean {
        const currentSteps = this.extractNonEmptySteps(currentFormData);
        const originalSteps = this.extractNonEmptySteps(originalFormData);

        return JSON.stringify(currentSteps) !== JSON.stringify(originalSteps);
    }

    private extractNonEmptySteps(formData: FormData): Array<Step> {
        const steps: Array<Step> = [];
        
        // Get all steps indices
        const indices = new Set<string>();
        for (const [key] of formData.entries()) {
            const match = key.match(/steps-(\d+)-/);
            if (match) {
                indices.add(match[1]);
            }
        }
        
        indices.forEach(index => {
            const description = formData.get(`steps-${index}-description`) as string;
            // Only include steps with a desctiption (non-empty)
            if (description && description.trim() !== '') {
                const order = parseInt(formData.get(`steps-${index}-order`) as string, 10);
                const id = formData.get(`steps-${index}-id`) as string;

                const isDeleted = formData.get(`steps-${index}-DELETE`) === 'on';
                steps.push({
                    id: id ? parseInt(id, 10) : undefined,
                    description: description.trim(),
                    order: order,
                    isDeleted: isDeleted
                });
            }
        });
        return steps;
    }
    
    handleCreateSave(): void{
        // For create mode: saving to hidden form fields
        console.log('Handling create save - saving to hidden form');
        
        const saveStepCount = this.saveStepsToHiddenForm();
        const message = `${saveStepCount} steps saved to recipe form.`;
        this.showMessage(message);
    }


    private saveStepsToHiddenForm(): number| null {
        const mainForm = document.getElementById(`${this.config.mainFormId}`) as HTMLElement;
        if (!mainForm) {
            console.error('Main recipe form not found');
            return null;
        }

        // Get the steps hidden container
        const stepContainer = mainForm.querySelector('#steps-hidden') as HTMLElement;
        if (!stepContainer) {
            console.error('Steps hidden container not found');
            return null;
        }

        // Clear existing hidden inputs
        stepContainer.innerHTML = '';

        // Collect step data from modal
        const stepCards = this.htmlModal.querySelectorAll('.step-card');
        let index = 0;

        stepCards.forEach(card => {
            const stepForm = card.querySelector('.step-form') as HTMLElement;
            if (stepForm && !stepForm.hidden) {
                const description = stepForm.querySelector('textarea[name*="description"]') as HTMLTextAreaElement;
                
                console.log('Step form:', stepForm);
                if (description?.value) {
                    // Create hidden inputs for each step field
                    const order = stepForm.querySelector('input[name*="order"]') as HTMLInputElement;
                    super.createHiddenTextArea(stepContainer, `steps-${index}-description`, description.value);
                    super.createHiddenInput(stepContainer, `steps-${index}-order`, order.value || '', '');
                    super.createHiddenInput(stepContainer, `steps-${index}-DELETE`, 'false', 'hidden');
                    
                    index++;
                }
            }
        });

        // Add management form hidden inputs
        super.createHiddenInput(stepContainer, 'steps-TOTAL_FORMS', index.toString(), 'hidden');
        super.createHiddenInput(stepContainer, 'steps-INITIAL_FORMS', '0', 'hidden');
        super.createHiddenInput(stepContainer, 'steps-MIN_NUM_FORMS', '0', 'hidden');
        super.createHiddenInput(stepContainer, 'steps-MAX_NUM_FORMS', '1000', 'hidden');

        return index;
    }
}