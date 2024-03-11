let gridApi;
const formatter = new Intl.DateTimeFormat('en-US', { day: '2-digit', month: '2-digit', year: 'numeric' });

const groupColDefs = [
    {
        field: 'date',
        cellEditor: 'agDateStringCellEditor',
        suppressSpanHeaderHeight: true,
        // valueFormatter: (params) => { return (params.value) ? formatter.format(Date(params.value)) : null; },
        filterParams: {
            treeList: true,
        },
    }
];

const gridOptions = {
    pagination: true,
    columnDefs: groupColDefs,
    defaultColDef: {
        // flex:1,
        editable: false,
        filter: 'agSetColumnFilter',
        menuTabs: ['filterMenuTab'],
        floatingFilter: false,
    },
    alwaysShowHorizontalScroll: true,
    rowSelection: 'single',
    onFirstDataRendered: autoSizeAll,
    onColumnGroupOpened: autoSizeAll,
    debug: true,
};

function autoSizeAll(params) {

    gridApi.autoSizeColumns(
        gridApi.getAllGridColumns().filter(column => !column.colDef.suppressSizeToFit),
    );
};


document.getElementById("date_selector").style.visibility = 'visible';
// setup the grid after the page has finished loading
document.addEventListener('DOMContentLoaded', function () {
    var gridDiv = document.querySelector('#table');
    gridApi = agGrid.createGrid(gridDiv, gridOptions);
    updateData();
});

function updateData() {
    return fetch('/budget/data', {
            method: 'GET',
            })
        .then(httpResponse => httpResponse.json())
        .then(response => {
            for (let type of response.category_list) {
                let child_group = [{
                    headerName: 'Total',
                    columnGroupShow: 'closed',
                    valueGetter: aggSumFunc,
                }];
                for (let children of type.children) {
                    let child = {
                        field: children.name,
                        columnGroupShow: 'open',
                        filter: 'agNumberFilter',
                    }
                    child_group.push(child)
                }
                let newGroup = {
                    headerName: type.type,
                    children: child_group,
                    marryChildren: true,
                    // openByDefault: true,
                }
                groupColDefs.push(newGroup);
            }
            gridApi.setGridOption('columnDefs', groupColDefs)
            gridApi.setGridOption('rowData', response.budgets_list);
        })
        .catch(error => {
            console.error(error);
        })
    };

function aggSumFunc(params) {
    let sum = 0;
    for (let colData of params.column.parent.children){
        if (colData.colId in params.data ) {
            sum += params.data[colData.colId]
        }
    }
    return sum
}
