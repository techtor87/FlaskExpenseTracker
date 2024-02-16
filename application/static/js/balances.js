let gridApi;
const formatter = new Intl.DateTimeFormat('en-US', { day: '2-digit', month: '2-digit', year: 'numeric' });

const gridOptions = {
    autoSizeStrategy: {type: 'fitCellContents'},
    pagination: true,
    editType: 'fullRow',
    undoRedoCellEditing: true,
    undoRedoCellEditingLimit: 40,
    defaultColDef: {
        // flex:1,
        editable: true,
        filter: 'agSetColumnFilter',
        menuTabs: ['filterMenuTab'],
        floatingFilter: false
    },
    // Column Definitions: Defines & controls grid columns.
    columnDefs: [
        {
            field: 'id',
            hide: true,
            filterParams: {
                applyMiniFilterWhileTyping: true,
            },
        },
        {
            field: 'date',
            cellEditor: 'agDateStringCellEditor',
            // valueFormatter: (params) => { return (params.value) ? formatter.format(Date(params.value)) : null; },
            filterParams: {
                treeList: true,
            },
        },
        {
            field: 'bank',
            rowGroup: true,
            filterParams: {
                applyMiniFilterWhileTyping: true,
            },
        },
        {
            field: 'account',
            rowGroup: true,
        },
        {
            field: 'value',
            valueFormatter: (params) => { return (params.value) ? '$' + params.value.toLocaleString() : null; },
        },
        {
            field: 'retirement',
        },
        {
            field: 'type',
            cellEditor: 'agRichSelectCellEditor',
            cellEditorParams: {
                values: ['Checking', 'Savings', 'CD', 'Stock/Brokerage', 'Real Estate']
            },
            filterParams: {
                applyMiniFilterWhileTyping: true,
            },

        },
        {
            field: 'category',
            cellEditor: 'agRichSelectCellEditor',
            cellEditorParams: {
                values: ['Checking', 'Savings', 'CD', 'Stock/Brokerage', 'Real Estate']
            },
            filterParams: {
                applyMiniFilterWhileTyping: true,
            },
        },
    ],
    autoGroupColumnDef: {
        field: '',
        cellRenderer: 'agGroupCellRenderer',
    },
    groupDefaultExpanded: 1,
    rowSelection: 'single',
    onCellValueChanged: cellValueChanged,
    onGridReady: autoSizeAll,
    onFirstDataRendered: autoSizeAll,
    onGroupExpandedOrCollapsed: autoSizeAll,
    debug: true,
};

function autoSizeAll(params) {

    const colApi = params.columnApi;
    colApi.autoSizeColumns(
        colApi.getAllGridColumns().filter(column => !column.colDef.suppressSizeToFit),
    );
}

// setup the grid after the page has finished loading
document.addEventListener('DOMContentLoaded', function () {
    var gridDiv = document.querySelector('#table');
    gridApi = agGrid.createGrid(gridDiv, gridOptions);
    updateData();
});

function updateData() {
    return fetch('/account/data', {
            method: 'GET',
            })
        .then(httpResponse => httpResponse.json())
        .then(response => {
            gridApi.setGridOption('rowData', response.accounts_list);
        })
        .catch(error => {
            console.error(error);
        })
    };

function cellValueChanged(event) {
    var data = event.data;
    console.log('onRowValueChanged: ('+data+')')
    $.getJSON("/account/update", {'colId': event.column.colId, 'old_value': event.oldValue, 'new_data': JSON.stringify(data)},
    function( response ) {
        gridApi.setGridOption('rowData', response.accounts_list);
    });
    updateData();
}

function addRow() {
    console.log('Add Empty Row')
    gridApi.applyTransaction({ add: [{ }]});
}

function deleteRow() {
    var data = gridApi.getSelectedRows();
    console.log('deleteRow: ('+data+')')
    $.getJSON("/account/delete", {'delete_data': JSON.stringify(data)});
    updateData();
}
