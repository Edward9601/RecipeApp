import { RecipeManager } from './recipes.js';
import { SubRecipeManager } from './sub_recipes.js';
import { FilterPanelManager } from './filter_panel.js';
import { IngredientsManager } from './ingredients.js';
import { StepsManager } from './recipe_steps.js';

document.addEventListener('DOMContentLoaded', () => {
    new FilterPanelManager();
    if (document.getElementById('recipe-form')) {
        new RecipeManager();
    }
    if(document.getElementById('sub-recipe-form')){
        new SubRecipeManager();
    }

    if (document.getElementById('ingredients-modal-container')) {
        setUpModalAfterHtmxSwap('ingredientsModal', 'ingredients-modal-container', IngredientsManager);
    }

    if (document.getElementById('steps-modal-container')) {
        setUpModalAfterHtmxSwap('stepsModal', 'steps-modal-container', StepsManager);
    }
});

function setUpModalAfterHtmxSwap(modalId: string, containerId: string, managerClass: any) {
    if (document.getElementById(containerId)) {
        document.body.addEventListener('htmx:afterSwap', (event: Event) => {
            const customEvent = event as CustomEvent<{ target: HTMLElement }>;
            if (customEvent.detail && customEvent.detail.target.id === containerId) {
                new managerClass();
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