interface BaseRecipeItem{
    id: number;
    isDeleted: boolean;
}

export interface Step extends BaseRecipeItem {
    description: string;
    order: number
}

export interface Ingredient extends BaseRecipeItem {
    name: string;
    quantity: string;
    measurement: string; 
}


export interface FormManagerConfig{
    fieldPrefix: string;
    htmlModalId: string;
    htmlFormId: string;
    addButtonId: string;
    saveButtonId: string;
    removeButtonId: string;
    mainFormId: string;
    openModalButtonId: string;
    htmlDetailPageId: string
}