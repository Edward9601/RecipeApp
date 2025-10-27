import { RecipeManager } from './recipes.js';
import { FilterPanelManager } from './filter_panel.js';
import { IngredientsManager } from './ingredients.js';
import { StepsManager } from './recipe_steps.js';
import { RecipeObjectType } from './enums.js';
document.addEventListener('DOMContentLoaded', () => {
    new FilterPanelManager();
    const form = document.querySelector('#recipe-form, #sub-recipe-form');
    if (form) {
        new RecipeManager(form.id);
    }
    if (document.getElementById('ingredients-modal-container')) {
        const ingredientsConfig = BuildConfig(RecipeObjectType.INGREDIENT, form === null || form === void 0 ? void 0 : form.id);
        setUpModalAfterHtmxSwap('ingredientsModal', 'ingredients-modal-container', IngredientsManager, ingredientsConfig);
    }
    if (document.getElementById('steps-modal-container')) {
        const stepsConfig = BuildConfig(RecipeObjectType.STEP, form === null || form === void 0 ? void 0 : form.id);
        setUpModalAfterHtmxSwap('stepsModal', 'steps-modal-container', StepsManager, stepsConfig);
    }
});
function BuildConfig(objectType, mainFormId) {
    let detailPageId = undefined;
    if (mainFormId == undefined) {
        detailPageId = document.querySelector('.sub-recipe-detail-container') ?
            '.sub-recipe-detail-container' : '.recipe-detail-container';
    }
    switch (objectType) {
        case RecipeObjectType.INGREDIENT:
            return {
                fieldPrefix: "ingredient",
                htmlModalId: "ingredientsModal",
                htmlFormId: "ingredients-modal-from",
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
                htmlFormId: "steps-modal-from",
                addButtonId: "add-steps-button",
                saveButtonId: "save-steps-button",
                removeButtonId: ".remove-button",
                openModalButtonId: "openStepsButton",
                htmlDetailPageId: detailPageId || ".recipe-detail-container",
                htmxTargetId: "steps-modal-container"
            };
        default:
            throw new Error(`Unsupported object type: ${objectType}`);
    }
}
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