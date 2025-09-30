import { RecipeManager } from './recipes.js';
import { SubRecipeManager } from './sub_recipes.js';
import { FilterPanelManager } from './filter_panel.js';
import { IngredientsManager } from './ingredients.js';
import { StepsManager } from './recipe_steps.js';
const ingredientsConfig = {
    fieldPrefix: "ingredient",
    htmlModalId: "ingredientsModal",
    htmlFormId: "ingredients-modal-from",
    addButtonId: "add-ingredient-button",
    saveButtonId: "save-ingredients-button",
    removeButtonId: ".remove-button",
    mainFormId: "recipe-form",
    htmlDetailPageId: ".recipe-detail-container",
    openModalButtonId: "openIngredientsButton"
};
const stepsConfig = {
    fieldPrefix: "step",
    htmlModalId: "stepsModal",
    htmlFormId: "steps-modal-from",
    addButtonId: "add-steps-button",
    saveButtonId: "save-steps-button",
    removeButtonId: ".remove-button",
    mainFormId: "recipe-form",
    htmlDetailPageId: ".recipe-detail-container",
    openModalButtonId: "openStepsButton"
};
document.addEventListener('DOMContentLoaded', () => {
    new FilterPanelManager();
    if (document.getElementById('recipe-form')) {
        new RecipeManager();
    }
    if (document.getElementById('sub-recipe-form')) {
        new SubRecipeManager();
    }
    if (document.getElementById('ingredients-modal-container')) {
        setUpModalAfterHtmxSwap('ingredientsModal', 'ingredients-modal-container', IngredientsManager, ingredientsConfig);
    }
    if (document.getElementById('steps-modal-container')) {
        setUpModalAfterHtmxSwap('stepsModal', 'steps-modal-container', StepsManager, stepsConfig);
    }
});
function setUpModalAfterHtmxSwap(modalId, containerId, managerClass, config) {
    if (document.getElementById(containerId)) {
        document.body.addEventListener('htmx:afterSwap', (event) => {
            const customEvent = event;
            if (customEvent.detail && customEvent.detail.target.id === containerId) {
                new managerClass(config);
                const modalEl = document.getElementById(modalId);
                if (modalEl) {
                    const modal = new window.bootstrap.Modal(modalEl);
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
//# sourceMappingURL=main.js.map