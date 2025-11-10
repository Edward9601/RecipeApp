import { RecipeManager } from './recipes.js';
import { FilterPanelManager } from './filter_panel.js';
import { IngredientsManager } from './ingredients.js';
import { StepsManager } from './recipe_steps.js';
import { FormManagerConfig } from './interfaces/recipe_items_interfaces.js'
import { RecipeObjectType , RecipeType} from './enums.js';


document.addEventListener('DOMContentLoaded', () => {
    new FilterPanelManager();
    const form = document.querySelector('#recipe-form, #sub-recipe-form');
    if (form) {
        new RecipeManager(form.id);
    }

    if (document.getElementById('ingredients-modal-container')) {
        const ingredientsConfig = BuildConfig(RecipeObjectType.INGREDIENT, form?.id);
        setUpModalAfterHtmxSwap('ingredientsModal', 'ingredients-modal-container', IngredientsManager, ingredientsConfig);
    }

    if (document.getElementById('steps-modal-container')) {
        const stepsConfig = BuildConfig(RecipeObjectType.STEP, form?.id);
        setUpModalAfterHtmxSwap('stepsModal', 'steps-modal-container', StepsManager, stepsConfig);
    }
});


function BuildConfig(objectType: RecipeObjectType, mainFormId?: string): FormManagerConfig {
    let detailPageId: string | undefined = undefined;
    if (mainFormId == undefined) {
                detailPageId = document.querySelector('.sub-recipe-detail-container') ? 
                '.sub-recipe-detail-container' : '.recipe-detail-container';
            }
    switch (objectType) {
        case RecipeObjectType.INGREDIENT:
            return {
                    fieldPrefix: "ingredient",
                    htmlModalId: "ingredientsModal",
                    htmlFormId: "ingredients-modal-form",
                    addButtonId: "add-ingredient-button",
                    saveButtonId: "save-ingredients-button",
                    removeButtonId: ".remove-button",
                    openModalButtonId: "openIngredientsButton",
                    htmlDetailPageId: detailPageId || ".recipe-detail-container",
                    htmxTargetId: "ingredients-modal-container"
                };
        case RecipeObjectType.STEP:
            return {
                    fieldPrefix: "step",
                    htmlModalId: "stepsModal",
                    htmlFormId: "steps-modal-form",
                    addButtonId: "add-steps-button",
                    saveButtonId: "save-steps-button",
                    removeButtonId: ".remove-button",
                    openModalButtonId: "openStepsButton",
                    htmlDetailPageId:  detailPageId || ".recipe-detail-container",
                    htmxTargetId: "steps-modal-container"
                };
        default:
            throw new Error(`Unsupported object type: ${objectType}`);
    }
}

function setUpModalAfterHtmxSwap(modalId: string, 
    containerId: string, 
    managerClass: any, 
    config: FormManagerConfig) {
    if (document.getElementById(containerId)) {
        document.body.addEventListener('htmx:afterSwap', (event: Event) => {
            const customEvent = event as CustomEvent<{ target: HTMLElement }>;
            if (customEvent.detail && customEvent.detail.target.id === containerId) {
                new managerClass(config);
                const modalEl = document.getElementById(modalId);
                if (modalEl) {
                    const modal = new (window as any).bootstrap.Modal(modalEl);
                    modal.show();

                    modalEl.addEventListener('hidden.bs.modal', () => {
                        // Remove modal HTML
                        const container = document.getElementById(containerId);
                        if (container) {
                            container.innerHTML = '';
                        }
                        // Remove any leftover Bootstrap backdrops
                        document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
                        // Optionally, remove 'modal-open' class from body
                        document.body.classList.remove('modal-open');
                    }, { once: true });
                }
            }
        });
    }
}