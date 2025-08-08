import { RecipeManager } from './recipes.js';
import { SubRecipeManager } from './sub_recipes.js';
import { FilterPanelManager } from './filter_panel.js';
import { IngredientsManager } from './ingredients.js';
document.addEventListener('DOMContentLoaded', () => {
    new FilterPanelManager();
    if (document.getElementById('recipe-form')) {
        new RecipeManager();
    }
    if (document.getElementById('sub-recipe-form')) {
        new SubRecipeManager();
    }
    if (document.getElementById('ingredients-modal-container')) {
        document.body.addEventListener('htmx:afterSwap', (event) => {
            const customEvent = event;
            if (customEvent.detail && customEvent.detail.target.id === 'ingredients-modal-container') {
                new IngredientsManager();
                const modalEl = document.getElementById('ingredientsModal');
                if (modalEl) {
                    // @ts-ignore
                    const modal = new window.bootstrap.Modal(modalEl);
                    modal.show();
                    modalEl.addEventListener('hidden.bs.modal', () => {
                        // Remove modal HTML
                        const container = document.getElementById('ingredients-modal-container');
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
});
//# sourceMappingURL=main.js.map