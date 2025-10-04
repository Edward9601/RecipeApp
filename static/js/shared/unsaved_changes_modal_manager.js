export class UnsavedChangesModalManager {
    constructor() {
        this.modal = document.getElementById('unsavedChangesModal');
        if (this.modal) {
            this.saveChangesBtn = document.getElementById('save-changes-btn');
            this.discardChangesBtn = document.getElementById('discard-changes-btn');
            this.cancelButton = document.getElementById('cancel-close-btn');
            this.setUpEventListener();
        }
        else {
            console.log('Unsaved changes modal was not found.');
        }
    }
    setUpEventListener() {
        this.saveChangesBtn.addEventListener('click', () => {
            this.hide();
            if (this.saveCallback) {
                this.saveCallback();
            }
        });
        this.discardChangesBtn.addEventListener('click', () => {
            this.hide();
            if (this.discardCallback) {
                this.discardCallback();
            }
        });
        this.cancelButton.addEventListener('click', () => {
            this.hide();
        });
    }
    static getInstance() {
        if (!UnsavedChangesModalManager.instance) {
            UnsavedChangesModalManager.instance = new UnsavedChangesModalManager();
        }
        return UnsavedChangesModalManager.instance;
    }
    hide() {
        const bootstrapModal = window.bootstrap.Modal.getInstance(this.modal);
        if (bootstrapModal) {
            bootstrapModal.hide();
            document.body.classList.remove('modal-open');
            document.querySelectorAll('.modal-backdrop').forEach((el) => el.remove());
        }
    }
    show(saveCallback, discardCallback) {
        this.discardCallback = discardCallback;
        this.saveCallback = saveCallback;
        const bootstrapModal = new window.bootstrap.Modal(this.modal);
        if (bootstrapModal) {
            bootstrapModal.show();
        }
    }
}
//# sourceMappingURL=unsaved_changes_modal_manager.js.map