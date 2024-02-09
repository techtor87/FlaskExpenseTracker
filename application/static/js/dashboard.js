
const income_vs_expense_options = {
    // Container: HTML Element to hold the chart
    container: document.getElementById('income_vs_expense_canvas'),
    title: {text: 'Income vs Expense'},
    // Data: Data to be displayed in the chart
    // data: JSON.parse(income_expense_data),
    // Series: Defines which chart type and data to use
    series: [
        {
            type: 'area',
            xkey: 'date',
            ykey: 'income',
            yName: 'Income',
        },
        {
            type: 'area',
            xkey: 'date',
            ykey: 'expense',
            yName: 'Expense',
        },
        {
            type: 'line',
            xkey: 'date',
            ykey: 'total',
            yName: 'Total',
        }
    ],
    axes: [
        {
            type: "category",
            position: "bottom",
        },
        {
            type: "number",
            position: "left",

        }
    ]
};

const expense_vs_category_options = {
    // Container: HTML Element to hold the chart
    container: document.getElementById('expense_vs_category_canvas'),
    title: {text: 'Expenses by Category'},
    // Series: Defines which chart type and data to use
    series: [
        {
            // data: JSON.parse( income_category_data ),
            type: 'pie',
            angleKey: 'total',
            sectorLabelKey: 'category',
            outerRadiusRatio: 0.8,
            innerRadiusRatio: 0.6,
            fillOpacity: 0.5,
        },
        {
            // data: JSON.parse( income_category_data ),
            type: 'pie',
            angleKey: 'total',
            sectorLabelKey: 'category',
            outerRadiusRatio: 0.6,
            innerRadiusRatio: 0.4,
            fillOpacity: 0.5,
        },
    ],
};

const overtime_expenditure_options = {
    // Container: HTML Element to hold the chart
    container: document.getElementById('overtime_expenditure_canvas'),
    title: {text: 'Expense over Time'},
    // Data: Data to be displayed in the chart
    // data: JSON.parse( over_time_expenditure ),
    theme: {
        overrides: {
            line: {
                series: {
                    lineDash: [12, 3],
                    marker: {
                        enabled: false,
                    },
                },
            },
        },
    },
    // Series: Defines which chart type and data to use
    series: [
        {
            type: 'line',
            xKey: 'date',
            yKey: 'total'
        }
    ],
};

const income_expense_chart = agCharts.AgCharts.create(income_vs_expense_options);
const expense_category_chart = agCharts.AgCharts.create(expense_vs_category_options);
const time_expense_chart = agCharts.AgCharts.create(overtime_expenditure_options);

function update_page_data(res) {
    console.log('page loaded. getting data...');

    let start_date = document.getElementById('start_date').value
    let end_date = document.getElementById('end_date').value

    let ajax = $.ajax({
        type: "POST",
        url: `/dashboard/data`,
        contentType: "application/json;charset=UTF-8",
        data: JSON.stringify({
            'start_date': start_date,
            'end_date': end_date,
        }),
    })

    ajax.done(function(res){
        if (res)
            console.log("data received.");

            income_expense_chart.data = res.income_expense_data;
            expense_category_chart.data = res.income_category_data;
            time_expense_chart.data = res.over_time_expenditure;
    })
}
