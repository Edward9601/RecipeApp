export class UnsavedChangesModalManager {

    private static instance: UnsavedChangesModalManager;
    private readonly modal!: HTMLElement;
    private readonly saveChangesBtn!: HTMLButtonElement;
    private readonly discardChangesBtn!: HTMLButtonElement;
    private readonly cancelButton!: HTMLButtonElement;


    private saveCallback?: () => void;
    private discardCallback?: ()=> void;

    private constructor(){

        this.modal = document.getElementById('unsavedChangesModal') as HTMLElement;
        if(this.modal){

            this.saveChangesBtn = document.getElementById('save-changes-btn') as HTMLButtonElement;
            this.discardChangesBtn = document.getElementById('discard-changes-btn') as HTMLButtonElement;
            this.cancelButton = document.getElementById('cancel-close-btn') as HTMLButtonElement;
            this.setUpEventListener();
        }
        else{
            console.log('Unsaved changes modal was not found.')
        }
    }

    private setUpEventListener():void {
        this.saveChangesBtn.addEventListener('click', ()=> {
            this.hide();
            if(this.saveCallback){
                this.saveCallback();
            }
        })
        this.discardChangesBtn.addEventListener('click', ()=>{
            this.hide()
            if(this.discardCallback){
                this.discardCallback();
            }
        })
        this.cancelButton.addEventListener('click', ()=> {
            this.hide();
        })
    }

    public static getInstance():UnsavedChangesModalManager{
        if(!UnsavedChangesModalManager.instance){
            UnsavedChangesModalManager.instance = new UnsavedChangesModalManager()
        }
        return UnsavedChangesModalManager.instance;
    }

    hide():void {
        const bootstrapModal = (window as any).bootstrap.Modal.getInstance(this.modal);
        if(bootstrapModal){
            bootstrapModal.hide()

            document.body.classList.remove('modal-open');
            document.querySelectorAll('.modal-backdrop').forEach((el) => el.remove());
        }
    }

    show(saveCallback: ()=> void, discardCallback: ()=> void):void {
        this.discardCallback = discardCallback;
        this.saveCallback = saveCallback;

        const bootstrapModal = new (window as any).bootstrap.Modal(this.modal);
        if(bootstrapModal){
            bootstrapModal.show();
        }
    }
}