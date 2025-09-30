import { UnsavedChangesModalManager } from "../shared/unsaved_changes_modal_manager.js";
export class BaseFormManager {
    constructor(config) {
        var _a, _b;
        this.unsavedChangesManager = UnsavedChangesModalManager.getInstance();
        this.isUpdateMode = null;
        this.hasUnsavedChanges = false;
        this.reloadItems = false;
        this.originalFormData = null;
        this.detailPage = null;
        this.config = config;
        this.htmlModal = document.getElementById(config.htmlModalId);
        if (this.htmlModal) {
            this.htmlForm = document.getElementById(config.htmlFormId);
            this.addButton = document.getElementById(config.addButtonId);
            this.saveButton = document.getElementById(config.saveButtonId);
            this.detailPage = document.querySelector(config.htmlDetailPageId);
            this.isUpdateMode = ((_b = (_a = this.saveButton) === null || _a === void 0 ? void 0 : _a.getAttribute('data-mode')) === null || _b === void 0 ? void 0 : _b.match(/update/i)) ? true : false;
            this.originalFormData = this.getFormData(this.htmlForm);
            this.setupHtmxInterception(this.htmlModal);
        }
    }
    getFormData(htmlForm) {
        return new FormData(htmlForm);
    }
    getCSRFToken() {
        const cookieCRSFTokenMatch = document.cookie.match(/csrftoken=([^;]+)/);
        if (cookieCRSFTokenMatch) {
            return cookieCRSFTokenMatch[1];
        }
        console.error('CSRF token not found in cookies');
        return null;
    }
    setupHtmxInterception(htmlModal) {
        // Find the specific button that opens modal
        const openModalButton = document.getElementById(this.config.openModalButtonId);
        if (openModalButton) {
            openModalButton.addEventListener('htmx:beforeRequest', (event) => {
                // Prevent HTMX from sending the request
                if (!this.reloadItems) {
                    event.preventDefault();
                    const modal = new window.bootstrap.Modal(htmlModal);
                    modal.show();
                }
            });
        }
    }
    collectFormData() {
        const formData = new FormData(this.htmlForm);
        return formData;
    }
    checkForChanges(ingredientForm) {
        const currentFormData = new FormData(ingredientForm);
        this.hasUnsavedChanges = this.hasMeaningfulChanges(currentFormData, this.originalFormData);
    }
    showLoadingState() {
        const loader = document.querySelector('.loader');
        if (loader) {
            loader.classList.remove('loader-hidden');
        }
    }
    closeModal(modalElement) {
        const modal = window.bootstrap.Modal.getInstance(modalElement);
        if (modal) {
            this.originalFormData = this.getFormData(this.htmlForm);
            modal.hide();
            document.body.classList.remove('modal-open');
            document.querySelectorAll('.modal-backdrop').forEach((el) => el.remove());
        }
    }
    hideLoadingState() {
        const loader = document.querySelector('.loader');
        if (loader) {
            loader.classList.add('loader-hidden');
        }
    }
    showMessage(message) {
        const existingBox = document.getElementById('custom-message-box');
        if (existingBox)
            existingBox.remove();
        // Create overlay
        const overlay = document.createElement('div');
        overlay.id = 'custom-message-box';
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100vw';
        overlay.style.height = '100vh';
        overlay.style.background = 'rgba(0,0,0,0.4)';
        overlay.style.display = 'flex';
        overlay.style.alignItems = 'center';
        overlay.style.justifyContent = 'center';
        overlay.style.zIndex = '2000';
        // Create message box
        const box = document.createElement('div');
        box.style.background = '#fff';
        box.style.padding = '2rem';
        box.style.borderRadius = '8px';
        box.style.boxShadow = '0 2px 16px rgba(0,0,0,0.2)';
        box.style.textAlign = 'center';
        box.innerHTML = `
            <div style="margin-bottom: 1rem;">${message}</div>
            <button id="custom-message-ok" class="btn btn-primary">OK</button>`;
        overlay.appendChild(box);
        document.body.appendChild(overlay);
        // Close on OK button
        const okBtn = box.querySelector('#custom-message-ok');
        okBtn === null || okBtn === void 0 ? void 0 : okBtn.addEventListener('click', () => {
            overlay.remove();
        });
        // Close on click outside the box
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay)
                overlay.remove();
        });
    }
    createHiddenInput(container, name, value) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = name;
        input.value = value;
        container.appendChild(input);
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
    removeItemForm(button) {
        const itemCard = button.closest(`.${this.config.fieldPrefix}-card`);
        if (!itemCard)
            return;
        let itemForm = itemCard.querySelector(`.${this.config.fieldPrefix}-form`);
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
    setUpButtonsDelegationEventListeners(elementId) {
        const itemList = this.htmlModal.querySelector(elementId);
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
    SetUpModalEventListener() {
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
                }
                else {
                    this.handleCreateSave();
                }
            });
        }
    }
}
//# sourceMappingURL=base_recipe_item.js.map