export class FilterPanelManager {
    constructor() {
        console.log('Initializing FilterPanelManager');
        this.filtersButton = document.getElementById('filterDropdownBtn');
        this.filtersPanel = document.getElementById('filterDropdownPanel');
        if (this.filtersButton && this.filtersPanel) {
            this.setupFiltersButton();
        }
    }
    setupFiltersButton() {
        if (!this.filtersButton || !this.filtersPanel) {
            console.error('Filters button or panel not found.');
            return;
        }
        this.filtersButton.addEventListener('click', (event) => {
            var _a, _b, _c, _d;
            event.stopPropagation();
            if (!((_a = this.filtersPanel) === null || _a === void 0 ? void 0 : _a.classList.contains('open'))) {
                (_b = this.filtersPanel) === null || _b === void 0 ? void 0 : _b.classList.add('open');
                (_c = this.filtersButton) === null || _c === void 0 ? void 0 : _c.setAttribute('aria-expanded', 'true');
            }
            else {
                this.filtersPanel.classList.remove('open');
                (_d = this.filtersButton) === null || _d === void 0 ? void 0 : _d.setAttribute('aria-expanded', 'false');
            }
        });
        document.addEventListener('click', (event) => {
            var _a, _b, _c, _d;
            if (!((_a = this.filtersButton) === null || _a === void 0 ? void 0 : _a.contains(event.target)) &&
                !((_b = this.filtersPanel) === null || _b === void 0 ? void 0 : _b.contains(event.target))) {
                (_c = this.filtersPanel) === null || _c === void 0 ? void 0 : _c.classList.remove('open');
                (_d = this.filtersButton) === null || _d === void 0 ? void 0 : _d.setAttribute('aria-expanded', 'false');
            }
        });
    }
}
//# sourceMappingURL=filter_panel.js.map