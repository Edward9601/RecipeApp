export class FilterPanelManager {
    private filtersButton: HTMLButtonElement | null;
    private filtersPanel: HTMLElement | null;

    constructor() {
        console.log('Initializing FilterPanelManager');
        this.filtersButton = document.getElementById('filterDropdownBtn') as HTMLButtonElement;
        this.filtersPanel = document.getElementById('filterDropdownPanel');
        if (this.filtersButton && this.filtersPanel) {
            this.setupFiltersButton();
        }
    }

    private setupFiltersButton(): void {
        if (!this.filtersButton || !this.filtersPanel) {
            console.error('Filters button or panel not found.');
            return;
        }

        this.filtersButton.addEventListener('click', (event) => {
            event.stopPropagation();
            if (!this.filtersPanel?.classList.contains('open')) {
                this.filtersPanel?.classList.add('open');
                this.filtersButton?.setAttribute('aria-expanded', 'true');
            } else {
                this.filtersPanel.classList.remove('open');
                this.filtersButton?.setAttribute('aria-expanded', 'false');
            }
        });

        document.addEventListener('click', (event) => {
            if (
                !this.filtersButton?.contains(event.target as Node) &&
                !this.filtersPanel?.contains(event.target as Node)
            ) {
                this.filtersPanel?.classList.remove('open');
                this.filtersButton?.setAttribute('aria-expanded', 'false');
            }
        });
    }
}