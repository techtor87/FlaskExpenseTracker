let rulesGridApi;


const rulesGridOptions = {
    autoSizeStrategy: {type: 'fitCellContents'},
    pagination: true,
    // editType: 'fullRow',
    undoRedoCellEditing: true,
    undoRedoCellEditingLimit: 40,
    stopEditingWhenCellsLoseFocus: true,
    defaultColDef: {
        flex:1,
        editable: true,
        filter: true,
        floatingFilter: false
    },
    // Column Definitions: Defines & controls grid columns.
    columnDefs: [
        {
            field: 'id',
            hide: true,
        },
        {
            field: 'if_field',
            headerName: 'IF',
            cellEditor: 'agSelectCellEditor',
            cellEditorParams: {
                values: [
                    'category_id',
                    'date',
                    'description',
                    'amount',
                    'type',
                    'bank_account.bank.bank',
                    'bank_account.bank.account',
                    'CUSTOM_STATEMENT',
                ]
            },
            menuTabs: ['filterMenuTab'],
            minWidth: 50,
            filter: 'agSetColumnFilter',
            filterParams: {
                applyMiniFilterWhileTyping: true,
            },
        },
        {
            field: 'if_operation',
            headerName: '',
            cellEditor: 'agSelectCellEditor',
            cellEditorParams: {
                values: [
                    '==',
                    '!=',
                    '>',
                    '>=',
                    '<=',
                    '<',
                    'in',
                    'is',
                    'is not',
                    'not in',
                    ''
                ]
            },
            menuTabs: ['filterMenuTab'],
            minWidth: 50,
            filter: 'agSetColumnFilter',
            filterParams: {
                applyMiniFilterWhileTyping: true,
            },
        },
        {
            field: 'if_statement',
            headerName: 'Statement',
            minWidth: 50,
            menuTabs: ['filterMenuTab'],
            filter: 'agSetColumnFilter',
            cellEditorSelector: cellEditorSelector,
            filterParams: {
                applyMiniFilterWhileTyping: true,
            },
        },
        {
            field: 'then_field',
            headerName: 'THEN',
            cellEditor: 'agSelectCellEditor',
            cellEditorParams: {
                values: [
                    'category_id',
                    'date',
                    'description',
                    'amount',
                    'type',
                    'bank_account_id',
                ]
            },
            menuTabs: ['filterMenuTab'],
            minWidth: 50,
            filter: 'agSetColumnFilter',
            filterParams: {
                applyMiniFilterWhileTyping: true,
            },
        },
        {
            field: 'then_statement',
            headerName: 'Statement',
            minWidth: 50,
            menuTabs: ['filterMenuTab'],
            filter: 'agSetColumnFilter',
            cellEditorSelector: cellEditorSelector,
            filterParams: {
                applyMiniFilterWhileTyping: true,
            },
        },
    ],
    rowSelection: 'single',
    // onRowValueChanged: rowlValueChanged,
    onCellValueChanged: rowlValueChanged,
    debug: true,
};

// setup the grid after the page has finished loading
document.addEventListener('DOMContentLoaded', function () {
    var gridDiv = document.querySelector('#rules_table');
    rulesGridApi = agGrid.createGrid(gridDiv, rulesGridOptions);
    updateRulesData();
});

let categories;
function updateRulesData() {
    return fetch('/rules/data', {
            method: 'GET',
            })
        .then(httpResponse => httpResponse.json())
        .then(response => {
            categories = response.category_list;
            rulesGridApi.setGridOption('rowData', response.rules_list);
        })
        .catch(error => {
            console.error(error);
        })
    };

function rowlValueChanged(event) {
    var data = event.data;
    console.log('onRowValueChanged: ('+JSON.stringify(data)+')')
    $.post("/rules/update", {'new_data': JSON.stringify(data)});
    // updateRulesData();
}

function addRow() {
    console.log('Add Empty Row')
    rulesGridApi.applyTransaction({ add: [{ }]});
}

function deleteRow() {
    var data = rulesGridApi.getSelectedRows();
    console.log('deleteRow: ('+JSON.stringify(data)+')')
    $.post("/rules/delete", {'delete_data': JSON.stringify(data)});
    updateRulesData();
}

function cellEditorSelector(params) {
    let field;
    if (params.colDef.field === 'if_statement'){
        field = params.data.if_field;
    }
    else if (params.colDef.field === 'then_statement')
    {
        field = params.data.then_field;
    }

    if (field === 'category_id')
    {
        return {
            component: 'agRichSelectCellEditor',
            params: {
                values: Array.from(categories, (x) => x['name']),
            },
            allowTyping: true,
            highlightMatch: true,
        }
    }
    if (field === 'type')
    {
        return {
            component: 'agRichSelectCellEditor',
            params: {
                values: ['debit', 'credit']
            },
            allowTyping: true,
            highlightMatch: true,
        }
    }

    return {
        component: 'agTextCellEditor'
    }

}
