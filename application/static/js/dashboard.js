let USD = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
});
function moneyToolTipRenderer({datum, xKey, yKey}) {
    return {
        title: datum[xKey],
        content: USD.format(datum[yKey]),
    }
};

function moneyDoughnutToolTipRenderer({datum, angleKey}) {
    return {
        content: USD.format(datum[angleKey]),
    }
};

let monthlyTotal = 1;
function categoryTypeToolTipRenderer({datum, angleKey}) {
    return {
        content: (datum[angleKey]/monthlyTotal)*100 + '%',
    }
};

// setup the grid after the page has finished loading
document.addEventListener('DOMContentLoaded', function () {
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

            monthlyTotal = res.expense_category_data['category_type'].reduce((sum, num) => { return sum + num['total']; }, 0)
            let income_vs_expense_options = {
                // Container: HTML Element to hold the chart
                container: document.getElementById('income_vs_expense_canvas'),
                title: {text: 'Income vs Expense'},
                // Data: Data to be displayed in the chart
                data: res.income_expense_data,
                // Series: Defines which chart type and data to use
                series: [
                    {
                        type: 'area',
                        xKey: 'date',
                        yKey: 'income',
                        yName: 'Income',
                        tooltip: {
                            renderer: moneyToolTipRenderer
                        },
                    },
                    {
                        type: 'area',
                        xKey: 'date',
                        yKey: 'expense',
                        yName: 'Expense',
                        tooltip: {
                            renderer: moneyToolTipRenderer
                        },
                    },
                    {
                        type: 'line',
                        xKey: 'date',
                        yKey: 'total',
                        yName: 'Total',
                        tooltip: {
                            renderer: moneyToolTipRenderer
                        },
                    },
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
                ],
                navigator: {
                    enabled: true,
                    height: 15,
                },
            };

            let expense_vs_category_options = {
                // Container: HTML Element to hold the chart
                container: document.getElementById('expense_vs_category_canvas'),
                title: {text: 'Expenses by Category'},
                // Series: Defines which chart type and data to use
                series: [
                    {
                        data: res.expense_category_data['category'],
                        type: 'pie',
                        angleKey: 'total',
                        sectorLabelKey: 'category',
                        outerRadiusRatio: 1,
                        innerRadiusRatio: 0.7,
                        fillOpacity: 0.5,
                        tooltip: {
                            renderer: moneyDoughnutToolTipRenderer
                        },
                    },
                    {
                        data: res.expense_category_data['category_type'],
                        type: 'pie',
                        angleKey: 'total',
                        sectorLabelKey: 'type',
                        outerRadiusRatio: 0.7,
                        innerRadiusRatio: 0.4,
                        fillOpacity: 0.5,
                        tooltip: {
                            renderer: categoryTypeToolTipRenderer
                        },
                    },
                ],
            };

            let overtime_expenditure_options = {
                // Container: HTML Element to hold the chart
                container: document.getElementById('overtime_expenditure_canvas'),
                title: {text: 'Expense over Time'},
                // Data: Data to be displayed in the chart
                data: res.over_time_expenditure,
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
                        yKey: 'total',
                        tooltip: {
                            renderer: moneyToolTipRenderer
                        },
                    }
                ],
            };

            let net_worth_options = {
                // Container: HTML Element to hold the chart
                container: document.getElementById('net_worth_canvas'),
                title: {text: 'Account Balances over Time'},
                // Data: Data to be displayed in the chart
                data: res.net_worth_data,
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
                        yKey: 'checking',
                        yName: 'Ally - Checking',
                        tooltip: {
                            renderer: moneyToolTipRenderer
                        },
                    },
                    {
                        type: 'line',
                        xKey: 'date',
                        yKey: 'total',
                        yName: 'Net Worth',
                        tooltip: {
                            renderer: moneyToolTipRenderer
                        },
                    },
                ],
            };

            const income_expense_chart = agCharts.AgCharts.create(income_vs_expense_options);
            const expense_category_chart = agCharts.AgCharts.create(expense_vs_category_options);
            const time_expense_chart = agCharts.AgCharts.create(overtime_expenditure_options);
            const net_worth_chart = agCharts.AgCharts.create(net_worth_options);

    })
});
