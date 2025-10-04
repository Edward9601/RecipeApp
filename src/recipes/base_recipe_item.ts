import { FormManagerConfig } from './interfaces/recipe_items_interfaces.js'
import { UnsavedChangesModalManager } from "../shared/unsaved_changes_modal_manager.js";

export abstract class BaseFormManager<T> {

    protected config: FormManagerConfig;
    protected readonly htmlModal!: HTMLElement;
    protected readonly htmlForm!: HTMLFormElement;
    protected readonly addButton!: HTMLButtonElement;
    protected readonly saveButton!: HTMLButtonElement;
    protected readonly openModalButton!: HTMLButtonElement;
    protected readonly mainForm!: HTMLFormElement;
    protected unsavedChangesManager: UnsavedChangesModalManager = UnsavedChangesModalManager.getInstance()

    protected isUpdateMode: boolean | null = null;
    protected hasUnsavedChanges: boolean = false;
    protected reloadItems: boolean = false;
    protected originalFormData: FormData| null = null;
    protected readonly detailPage: HTMLElement | null = null;
    protected isBound: boolean = false;

    constructor(config: FormManagerConfig){
        this.config = config;

        this.htmlModal = document.getElementById(config.htmlModalId) as HTMLElement;
        if(this.htmlModal){
            this.htmlForm = document.getElementById(config.htmlFormId) as HTMLFormElement;
            this.addButton = document.getElementById(config.addButtonId) as HTMLButtonElement;
            this.saveButton = document.getElementById(config.saveButtonId) as HTMLButtonElement;
            this.detailPage = document.querySelector(config.htmlDetailPageId);
            this.mainForm = document.getElementById(config.mainFormId) as HTMLFormElement;
            this.isUpdateMode = this.saveButton?.getAttribute('data-mode')?.match(/update/i) ? true : false;
            this.originalFormData = this.getFormData(this.htmlForm);
            if(!this.isBound){
                this.templateInitialize();
                this.isBound = true;
            }
            
            
        }
    }

    protected templateInitialize(): void {
        this.setupHtmxInterception(this.htmlModal);
        this.setUpButtonsDelegationEventListeners();
        this.setUpModalCloseProtection(this.htmlModal, this.htmlForm);
    }


    protected setupHtmxInterception(htmlModal: HTMLElement): void {
        // Find the specific button that opens modal
        const openModalButton = document.getElementById(this.config.openModalButtonId);
    
    if (openModalButton) {
        openModalButton.addEventListener('htmx:beforeRequest', (event: Event) => {
            // Only prevent the request for initial modal opening
            const target = event.target as HTMLElement;
            if(!this.reloadItems && !target.classList.contains('has-validation-errors')){
                event.preventDefault();
                const modal = new (window as any).bootstrap.Modal(htmlModal);
                modal.show();
            }   
        });
    }
    }

    protected async setUpModalCloseProtection(htmlModal: HTMLElement, htmlForm: HTMLFormElement): Promise<void> {
        htmlModal.addEventListener('hide.bs.modal', (event) => {
            this.checkForChanges(htmlForm);
            if(this.hasUnsavedChanges){
                event.preventDefault();
                this.unsavedChangesManager.show(async ()=>{
                    const apiUrl = this.saveButton.dataset.url!;
                    this.hasUnsavedChanges = false;
                    await this.handleUpdateSave(apiUrl);
                    this.closeModal(this.htmlModal);
                },()=>{
                    this.reloadItems = true; // indicating to fetch data again on modal open
                    this.hasUnsavedChanges = false;
                    this.closeModal(this.htmlModal);
                }); 
            }
        })
    }

    

    protected getFormData(htmlForm: HTMLFormElement): FormData {
        return new FormData(htmlForm);
    }

    protected getCSRFToken(): string | null {
        const cookieCRSFTokenMatch = document.cookie.match(/csrftoken=([^;]+)/);
        if (cookieCRSFTokenMatch) {
            return cookieCRSFTokenMatch[1];
        }
        console.error('CSRF token not found in cookies');
        return null;
    }

    protected collectFormData(): FormData{
        const formData = new FormData(this.htmlForm);
        return formData;
    }

    protected checkForChanges(ingredientForm: HTMLFormElement): void {
        const currentFormData = new FormData(ingredientForm);
        this.hasUnsavedChanges = this.hasMeaningfulChanges(currentFormData, this.originalFormData!)
    }

    protected showLoadingState(): void {
        const loader = document.querySelector('.loader') as HTMLElement;
        if (loader) {
            loader.classList.remove('loader-hidden');
        }
    }

    protected closeModal(modalElement: HTMLElement): void {
        const modal = (window as any).bootstrap.Modal.getInstance(modalElement);
        if (modal) {
            this.originalFormData = this.getFormData(this.htmlForm);
            modal.hide();

            document.body.classList.remove('modal-open');
            document.querySelectorAll('.modal-backdrop').forEach((el) => el.remove());
        }
    }

    protected hideLoadingState(): void {
       const loader = document.querySelector('.loader') as HTMLElement;
        if (loader) {
            loader.classList.add('loader-hidden');
        }
    }

    protected showMessage(message: string): void {

        const existingBox = document.getElementById('custom-message-box');
        if (existingBox) existingBox.remove();

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
        const okBtn = box.querySelector('#custom-message-ok') as HTMLButtonElement;
        okBtn?.addEventListener('click', () => {
            overlay.remove();
        });

        // Close on click outside the box
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) overlay.remove();
        });
    }

    protected createHiddenInput(container: HTMLElement, name: string, value: string, inputType: string): void {
        const input = document.createElement('input');
        input.type = inputType;
        input.name = name;
        input.value = value;
        container.appendChild(input);
    }

    protected createHiddenTextArea(container: HTMLElement, name: string, value: string): void {
        const textArea = document.createElement('textarea');
        textArea.name = name;
        textArea.value = value;
        textArea.style.display = 'none';
        container.appendChild(textArea);
    }


    protected SetUpModalEventListener(){

        document.body.addEventListener('htmx:afterSwap', (event: Event) => {
            // Cast to CustomEvent with detail property
            const customEvent = event as CustomEvent<{ target: HTMLElement }>;
            if (customEvent.detail && customEvent.detail.target.id === this.config.htmxTargetId) {
                const modalEl = document.getElementById(this.config.htmlModalId) as HTMLElement;
                if (modalEl) {
                    const modal = new (window as any).bootstrap.Modal(modalEl);
                    modal.show();
                }}
            });
    }

    protected abstract setUpButtonsDelegationEventListeners(): void;
    protected abstract addItemToForm(): void;
    protected abstract removeItemForm(button: HTMLElement): void;
    protected abstract hasMeaningfulChanges(currentFormData: FormData, originalFormData: FormData): boolean;
    protected abstract handleUpdateSave(apiUrl: string): Promise<void>;
    protected abstract handleCreateSave(): void;


}