import { RecipeManager } from './recipes.js';
import { FilterPanelManager } from './filter_panel.js';
import { IngredientsManager } from './ingredients.js';
import { StepsManager } from './recipe_steps.js';
import { FormManagerConfig } from './interfaces/recipe_items_interfaces.js'

const form = document.querySelector('#recipe-form, #sub-recipe-form');
const ingredientsConfig: FormManagerConfig = {
    fieldPrefix: "ingredient",
    htmlModalId: "ingredientsModal",
    htmlFormId: "ingredients-modal-from",
    addButtonId: "add-ingredient-button",
    saveButtonId: "save-ingredients-button",
    removeButtonId: ".remove-button",
    mainFormId: form!.id || "recipe-form",
    htmlDetailPageId: ".recipe-detail-container",
    openModalButtonId: "openIngredientsButton",
    htmxTargetId: "ingredients-modal-container"

}


const stepsConfig: FormManagerConfig = {
    fieldPrefix: "step",
    htmlModalId: "stepsModal",
    htmlFormId: "steps-modal-from",
    addButtonId: "add-steps-button",
    saveButtonId: "save-steps-button",
    removeButtonId: ".remove-button",
    mainFormId: form!.id || "recipe-form",
    htmlDetailPageId: ".recipe-detail-container",
    openModalButtonId: "openStepsButton",
    htmxTargetId: "steps-modal-container"

}

document.addEventListener('DOMContentLoaded', () => {
    new FilterPanelManager();
    if (form) {
        new RecipeManager(form.id);
    }

    if (document.getElementById('ingredients-modal-container')) {
        setUpModalAfterHtmxSwap('ingredientsModal', 'ingredients-modal-container', IngredientsManager, ingredientsConfig);
    }

    if (document.getElementById('steps-modal-container')) {
        setUpModalAfterHtmxSwap('stepsModal', 'steps-modal-container', StepsManager, stepsConfig);
    }
});

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