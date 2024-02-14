let gridApi;

const gridOptions = {
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
            field: 'name',
            minWidth: 200,
            menuTabs: ['filterMenuTab'],
            filter: 'agSetColumnFilter',
            filterParams: {
                applyMiniFilterWhileTyping: true,
            },
        },
        {
            rowGroup: true,
            field: 'type',
            minWidth: 200,
            menuTabs: ['filterMenuTab'],
            filter: 'agSetColumnFilter',
            filterParams: {
                applyMiniFilterWhileTyping: true,
            },
        },
    ],
    autoGroupColumnDef: {
        headerName: 'Category Type',
        field: '',
        cellRenderer: 'agGroupCellRenderer',
    },
    groupDefaultExpanded: 1,
    rowSelection: 'single',
    onCellValueChanged: cellValueChanged,
    debug: true,
};

// setup the grid after the page has finished loading
document.addEventListener('DOMContentLoaded', function () {
    var gridDiv = document.querySelector('#table');
    gridApi = agGrid.createGrid(gridDiv, gridOptions);
    updateData();
});

function updateData() {
    return fetch('/category/data', {
            method: 'GET',
            })
        .then(httpResponse => httpResponse.json())
        .then(response => {
            gridApi.setGridOption('rowData', response.category_list);
        })
        .catch(error => {
            console.error(error);
        })
    };

function cellValueChanged(event) {
    var data = event.data;
    console.log('onRowValueChanged: ('+data+')')
    $.getJSON("/category/update", {'old_value': event.oldValue, 'new_data': JSON.stringify(data)});
    updateData();
}

function addRow() {
    console.log('Add Empty Row')
    gridApi.applyTransaction({ add: [{ }]});
}

function deleteRow() {
    var data = gridApi.getSelectedRows();
    console.log('deleteRow: ('+data+')')
    $.getJSON("/category/delete", {'delete_data': JSON.stringify(data)});
    updateData();
}
