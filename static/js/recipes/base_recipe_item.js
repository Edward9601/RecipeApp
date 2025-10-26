var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { UnsavedChangesModalManager } from "../shared/unsaved_changes_modal_manager.js";
export class BaseFormManager {
    constructor(config) {
        var _a, _b;
        this.unsavedChangesManager = UnsavedChangesModalManager.getInstance();
        this.mainForm = null;
        this.isUpdateMode = null;
        this.isCreateMode = false;
        this.isDetailPage = null;
        this.hasUnsavedChanges = false;
        this.reloadItems = false;
        this.originalFormData = null;
        this.recipeType = 'recipe';
        this.isBound = false;
        this.config = config;
        this.htmlModal = document.getElementById(config.htmlModalId);
        this.htmlForm = document.getElementById(config.htmlFormId);
        this.addButton = document.getElementById(config.addButtonId);
        this.saveButton = document.getElementById(config.saveButtonId);
        this.isDetailPage = document.querySelector(config.htmlDetailPageId);
        this.isCreateMode = !this.isDetailPage;
        this.isUpdateMode = ((_b = (_a = this.saveButton) === null || _a === void 0 ? void 0 : _a.getAttribute('data-mode')) === null || _b === void 0 ? void 0 : _b.match(/update/i)) ? true : false;
        this.originalFormData = this.getFormData(this.htmlForm);
        if (!this.isBound) {
            this.templateInitialize();
            this.detectContext();
            this.isBound = true;
        }
    }
    detectContext() {
        // Detect main form
        this.mainForm = document.querySelector('#recipe-form, #sub-recipe-form');
        // Detect recipe type
        if (this.mainForm) {
            this.recipeType = this.mainForm.id === 'sub-recipe-form' ? 'sub_recipe' : 'recipe';
        }
        else {
            // Check URL or page content for recipe type
            this.recipeType = window.location.pathname.includes('sub-recipes') ? 'sub_recipe' : 'recipe';
        }
    }
    templateInitialize() {
        this.setupHtmxInterception(this.htmlModal);
        this.setUpButtonsDelegationEventListeners();
        this.setUpModalCloseProtection(this.htmlModal, this.htmlForm);
    }
    setupHtmxInterception(htmlModal) {
        // Find the specific button that opens modal
        const openModalButton = document.getElementById(this.config.openModalButtonId);
        if (openModalButton) {
            openModalButton.addEventListener('htmx:beforeRequest', (event) => {
                // Only prevent the request for initial modal opening
                const target = event.target;
                if (!this.reloadItems && !target.classList.contains('has-validation-errors')) {
                    event.preventDefault();
                    const modal = new window.bootstrap.Modal(htmlModal);
                    modal.show();
                }
            });
        }
    }
    setUpModalCloseProtection(htmlModal, htmlForm) {
        return __awaiter(this, void 0, void 0, function* () {
            htmlModal.addEventListener('hide.bs.modal', (event) => {
                this.checkForChanges(htmlForm);
                if (this.hasUnsavedChanges) {
                    event.preventDefault();
                    this.unsavedChangesManager.show(() => __awaiter(this, void 0, void 0, function* () {
                        const apiUrl = this.saveButton.dataset.url;
                        this.hasUnsavedChanges = false;
                        yield this.handleUpdateSave(apiUrl);
                        this.closeModal(this.htmlModal);
                    }), () => {
                        this.reloadItems = true; // indicating to fetch data again on modal open
                        this.hasUnsavedChanges = false;
                        this.closeModal(this.htmlModal);
                    });
                }
            });
        });
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
    createHiddenInput(container, name, value, inputType) {
        const input = document.createElement('input');
        input.type = inputType;
        input.name = name;
        input.value = value;
        container.appendChild(input);
    }
    createHiddenTextArea(container, name, value) {
        const textArea = document.createElement('textarea');
        textArea.name = name;
        textArea.value = value;
        textArea.style.display = 'none';
        container.appendChild(textArea);
    }
    SetUpModalEventListener() {
        document.body.addEventListener('htmx:afterSwap', (event) => {
            // Cast to CustomEvent with detail property
            const customEvent = event;
            if (customEvent.detail && customEvent.detail.target.id === this.config.htmxTargetId) {
                const modalEl = document.getElementById(this.config.htmlModalId);
                if (modalEl) {
                    const modal = new window.bootstrap.Modal(modalEl);
                    modal.show();
                }
            }
        });
    }
}
//# sourceMappingURL=base_recipe_item.js.map