let gridApi;

const gridOptions = {
    autoSizeStrategy: {type: 'fitCellContents'},
    pagination: true,
    editType: 'fullRow',
    undoRedoCellEditing: true,
    undoRedoCellEditingLimit: 40,
    defaultColDef: {
        editable: true,
        filter: true,
        floatingFilter: false
    },
    // Column Definitions: Defines & controls grid columns.
    columnDefs: [
        {
            field: 'id',
            filter: false,
            editable: false,
        },
        {
            field: 'date',
            cellEditor: 'agDateStringCellEditor',
            menuTabs: ['filterMenuTab'],
            filter: 'agSetColumnFilter',
            filterParams: {
                treeList: true,
                // values: ,
                // keyCreator: ,
                // valueFormatter: ,
                // comparator: ,
            },
        },
        {
            field: 'description',
            flex: 3,
            menuTabs: ['filterMenuTab'],
            filter: 'agSetColumnFilter',
            filterParams: {
                applyMiniFilterWhileTyping: true,
                // values: ,
                // keyCreator: ,
                // valueFormatter: ,
                // comparator: ,
            },
        },
        {
            field: 'amount',
            flex: 1,
            valueFormatter: (params) => { return '$' + params.value.toLocaleString(); },
            menuTabs: ['filterMenuTab'],
            filter: 'agSetColumnFilter',
            filterParams: {
                // values: ,
                // keyCreator: ,
                // valueFormatter: ,
                // comparator: ,
            },
        },
        {
            field: 'type',
            cellEditor: 'agSelectCellEditor',
            cellEditorParams: {
                values: ['credit', 'debit']
            },
            menuTabs: ['filterMenuTab'],
            filter: 'agSetColumnFilter',
            filterParams: {
                // values: ,
                // keyCreator: ,
                // valueFormatter: ,
                // comparator: ,
            },
        },
        {
            field: 'category',
            cellEditor: 'agRichSelectCellEditor',
            cellEditorParams: {
                values: getCategories()
            },
            menuTabs: ['filterMenuTab'],
            filter: 'agSetColumnFilter',
            filterParams: {
                applyMiniFilterWhileTyping: true,
                // values: params => getCategoriesAsync(params),
                // keyCreator: ,
                // valueFormatter: ,
                // comparator: ,
            },
        },
        {
            field: 'account',
            flex: 1.5,
            menuTabs: ['filterMenuTab'],
            filter: 'agSetColumnFilter',
            filterParams: {
                applyMIniFilterWhileTyping: true,
                // values: ,
                // keyCreator: ,
                // valueFormatter: ,
                // comparator: ,
            },
        },
        {
            field: 'bank',
            flex: 2,
            menuTabs: ['filterMenuTab'],
            filter: 'agSetColumnFilter',
            filterParams: {
                applyMiniFilterWhileTyping: true,
                // values: ,
                // keyCreator: ,
                // valueFormatter: ,
                // comparator: ,
            },
        },
    ],
    onRowValueChanged: onRowValueChanged,
    debug: true,
};

function getCategoriesAsync(params) {
    fetch('/categories', {
            method: 'GET',
        })
    .then(httpResponse => httpResponse.json())
    .then(response => {
        return params.success(response.categories);
    })
    .catch(error => {
        console.error(error);
    })
};

function getCategories(params) {
    return fetch('/categories', {
            method: 'GET',
        })
        .then(httpResponse => httpResponse.json() )
        .then(response => {
            console.log(response.categories);
            return response.categories;
        })
    };

// setup the grid after the page has finished loading
document.addEventListener('DOMContentLoaded', function () {
    var gridDiv = document.querySelector('#table');
    gridApi = agGrid.createGrid(gridDiv, gridOptions);
});

const getData = fetch('/data_client/' + document.getElementById('start_date').value + '/'+document.getElementById('end_date').value, {
            method: 'GET',
            })
        .then(httpResponse => httpResponse.json())
        .then(response => {
            gridApi.setGridOption('rowData', response.rows);
        })
        .catch(error => {
            console.error(error);
        })


function getLastRowIndex(request, results) {
    if (!results) return undefined;
    var currentLastRow = (request.startRow || 0) + results.length;

    // if on or after the last block, work out the last row, otherwise return 'undefined'
    return currentLastRow < (request.endRow || 0) ? currentLastRow : undefined;
}

function onRowValueChanged(event) {
    var data = event.data;
    console.log('onRowValueChanged: ('+data+')')
    $.getJSON("/update", {'new_data': JSON.stringify(data)});
}
