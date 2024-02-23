let rulesGridApi;

const rulesGridOptions = {
    autoSizeStrategy: {type: 'fitCellContents'},
    pagination: true,
    editType: 'fullRow',
    undoRedoCellEditing: true,
    undoRedoCellEditingLimit: 40,
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
                ]
            },
            menuTabs: ['filterMenuTab'],
            minWidth: 200,
            filter: 'agSetColumnFilter',
            filterParams: {
                applyMiniFilterWhileTyping: true,
            },
        },
        {
            field: 'if_operation',
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
                    'not in'
                ]
            },
            menuTabs: ['filterMenuTab'],
            minWidth: 200,
            filter: 'agSetColumnFilter',
            filterParams: {
                applyMiniFilterWhileTyping: true,
            },
        },
        {
            field: 'if_statement',
            minWidth: 200,
            menuTabs: ['filterMenuTab'],
            filter: 'agSetColumnFilter',
            filterParams: {
                applyMiniFilterWhileTyping: true,
            },
        },
        {
            field: 'then_field',
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
            minWidth: 200,
            filter: 'agSetColumnFilter',
            filterParams: {
                applyMiniFilterWhileTyping: true,
            },
        },
        {
            field: 'then_statement',
            minWidth: 200,
            menuTabs: ['filterMenuTab'],
            filter: 'agSetColumnFilter',
            filterParams: {
                applyMiniFilterWhileTyping: true,
            },
        },
    ],
    rowSelection: 'single',
    onRowValueChanged: cellValueChanged,
    debug: true,
};

// setup the grid after the page has finished loading
document.addEventListener('DOMContentLoaded', function () {
    var gridDiv = document.querySelector('#rules_table');
    rulesGridApi = agGrid.createGrid(gridDiv, rulesGridOptions);
    updateRulesData();
});

function updateRulesData() {
    return fetch('/rules/data', {
            method: 'GET',
            })
        .then(httpResponse => httpResponse.json())
        .then(response => {
            rulesGridApi.setGridOption('rowData', response.rules_list);
        })
        .catch(error => {
            console.error(error);
        })
    };

function cellValueChanged(event) {
    var data = event.data;
    console.log('onRowValueChanged: ('+data+')')
    $.getJSON("/rules/update", {'new_data': JSON.stringify(data)});
    updateRulesData();
}

function addRow() {
    console.log('Add Empty Row')
    rulesGridApi.applyTransaction({ add: [{ }]});
}

function deleteRow() {
    var data = rulesGridApi.getSelectedRows();
    console.log('deleteRow: ('+data+')')
    $.getJSON("/rules/delete", {'delete_data': JSON.stringify(data)});
    updateRulesData();
}
