import json
from datetime import datetime

from dateutil.relativedelta import relativedelta
from flask import Blueprint, session, flash, redirect, render_template, request, url_for, jsonify, abort, make_response
from sqlalchemy import func, select, update, delete, text

from application import db
from application.form import BulkDataForm, UserDataForm
from application.models import Transactions, Category

bp = Blueprint('bp_transactions', __name__)

@bp.route("/transactions", methods=["GET", "POST"])
def transactions_view():
    if form_date := request.form.get("start_date"):
        session['start_date'] = form_date
    else:
        session['start_date'] = datetime.strftime(datetime.now(), "%Y-%m")

    if form_date := request.form.get("end_date"):
        session['end_date'] = form_date
    else:
        session['end_date'] = datetime.strftime(datetime.now() + relativedelta(months=1), "%Y-%m")


    entries = Transactions.query.filter(
        Transactions.date >= datetime.strptime(session['start_date'], "%Y-%m"),
        Transactions.date < datetime.strptime(session['end_date'], "%Y-%m")
    )
    return render_template("transactions.html", entries=entries)

@bp.route('/api/categories')
def get_categories():
    category_list = [(r._asdict())['name'] for r in db.session.execute(
        select(Category.name)
        ).all()]
    return jsonify(categories=category_list)


@bp.route('/api/update')
def update_row():
    new_data = json.loads(request.args.get('new_data'))
    db.session.execute(
        update(Transactions)
        .where(Transactions.id==new_data['id'])
        .values({
            "date": datetime.strptime(new_data['date'], '%a, %d %b %Y %H:%M:%S GMT'),
            "description": new_data['description'],
            "amount": new_data['amount'],
            "type": new_data['type'],
            "category_id": new_data['category_id'],
            # "account": new_data['account'],
            # "bank": new_data['bank']
        })
    )
    db.session.commit()
    return jsonify()

@bp.route('/api/data_client', methods=['GET'])
def get_table_data_client():
    start_date = datetime.strptime(session['start_date'], "%Y-%m")
    end_date = datetime.strptime(session['end_date'], "%Y-%m")

    entries = Transactions.query.where((Transactions.date >= start_date) & (Transactions.date < end_date)).all()
    for r in entries:
        if r.bank_account:
            r.bank = r.bank_account.bank.bank
            r.account = r.bank_account.bank.account
    rows = [r.as_dict() for r in entries]

    return jsonify(rows=rows)

@bp.route('/api/data', methods=['GET'])
def get_table_data():
    start_date = datetime.strptime(session['start_date'], "%Y-%m")
    end_date = datetime.strptime(session['end_date'], "%Y-%m")

    entries = db.session.execute(buildSql(request.json),
        {
            'start_date': start_date,
            'end_date': end_date
        }).all()

    rowCount = getRowCount(request, entries)
    resultsForPage = cutResultsToPageSize(request, entries)

    return jsonify(rows=[r._asdict() for r in resultsForPage],
                   lastRow=rowCount
    )

def buildSql(request):
    return text(createSelectSql(request)
        + ' FROM transactions'
        + createWhereSql(request)
        + createGroupBySql(request)
        + createOrderBySql(request)
        + createLimitSql(request))

def getRowCount(request, results):
    if results is None or len(results) == 0:
        return None
    currentLastRow = request.json.get('startRow') + len(results)
    return currentLastRow if currentLastRow <= request.json.get('endRow') else -1

def createSelectSql(request):
    rowGroupCols = request.get('rowGroupCols')
    valueCols = request.get('valueCols')
    groupKeys = request.get('groupKeys')

    if isDoingGrouping(rowGroupCols, groupKeys):
        colsToSelect = []

        rowGroupCol = rowGroupCols[len(groupKeys)]

        for value_col in valueCols:
            colsToSelect.append(f"{value_col['aggFunc']}({value_col['field']}) as {value_col['field']}")

        return ' SELECT ' + colsToSelect.join(', ')

    return 'SELECT *'


def create_filter_sql(key, item):
    if item['filterType'] == 'text':
        return create_text_filter_sql(key, item)
    elif item['filterType'] == 'number':
        return create_number_filter_sql(key, item)
    elif item['filterType'] == 'set':
        return create_set_filter_sql(key, item)
    else:
        print(f"unknown filter type: {item['filterType']}")

def create_set_filter_sql(key, item):
    return ''

def create_number_filter_sql(key, item):
    item_type = item['type']
    item_filter = item['filter']
    item_filter_to = item.get('filterTo', None)

    if item_type == 'equals':
        return f"{key} = {item_filter}"
    elif item_type == 'notEqual':
        return f"{key} != {item_filter}"
    elif item_type == 'greaterThan':
        return f"{key} > {item_filter}"
    elif item_type == 'greaterThanOrEqual':
        return f"{key} >= {item_filter}"
    elif item_type == 'lessThan':
        return f"{key} < {item_filter}"
    elif item_type == 'lessThanOrEqual':
        return f"{key} <= {item_filter}"
    elif item_type == 'inRange':
        return f"({key} >= {item_filter} and {key} <= {item_filter_to})"
    else:
        print(f"unknown number filter type: {item_type}")
        return 'true'

def create_text_filter_sql(key, item):
    item_type = item['type']
    item_filter = item['filter']

    if item_type == 'equals':
        return f"{key} = '{item_filter}'"
    elif item_type == 'notEqual':
        return f"{key} != '{item_filter}'"
    elif item_type == 'contains':
        return f"{key} like '%{item_filter}%'"
    elif item_type == 'notContains':
        return f"{key} not like '%{item_filter}%'"
    elif item_type == 'startsWith':
        return f"{key} like '{item_filter}%'"
    elif item_type == 'endsWith':
        return f"{key} like '%{item_filter}'"
    else:
        print(f"unknown text filter type: {item_type}")
        return 'true'

def createWhereSql(request):
    row_group_cols = request['rowGroupCols']
    group_keys = request['groupKeys']
    filter_model = request.get('filterModel', {})

    where_parts = []

    if group_keys:
        for index, key in enumerate(group_keys):
            col_name = row_group_cols[index]['field']
            where_parts.append(f"{col_name} = '{key}'")

    if filter_model:
        for key, item in filter_model.items():
            where_parts.append(create_filter_sql(key, item))

    if where_parts:
        return ' WHERE date >= :start_date AND date < :end_date' + ' AND '.join(where_parts)
    else:
        return ' WHERE date >= :start_date AND date < :end_date'


def createLimitSql(request):
    if request.get('startRow') is None or request.get('endRow') is None:
        return ''

    startRow = request.get('startRow')
    endRow = request.get('endRow')
    pageSize = endRow -  startRow
    return f' LIMIT {pageSize} OFFSET {startRow}'

def createGroupBySql(request):
    rowGroupCols = request['rowGroupCols']
    groupKeys = request['groupKeys']

    if isDoingGrouping(rowGroupCols, groupKeys):
        colsToGroupBy = []

        rowGroupCol = rowGroupCols[len(groupKeys)]
        colsToGroupBy.append(rowGroupCol['field'])

        return ' group by ' + ', '.join(colsToGroupBy)
    else:
        # select all columns
        return ''

def createOrderBySql(request):
    rowGroupCols = request['rowGroupCols']
    groupKeys = request['groupKeys']
    sortModel = request['sortModel']

    sortParts = []
    if sortModel:
        groupColIds = [groupCol['id'] for groupCol in rowGroupCols][0:len(groupKeys) + 1]

        for item in sortModel:
            if isDoingGrouping(rowGroupCols, groupKeys) and item['colId'] not in groupColIds:
                pass
            else:
                sortParts.append(item['colId'] + ' ' + item['sort'])

    if len(sortParts) > 0:
        return ' ORDER BY ' + ', '.join(sortParts)
    else:
        return ''

def isDoingGrouping(rowGroupCols, groupKeys):
    return len(rowGroupCols) > len(groupKeys)

def cutResultsToPageSize(request, results):
    pageSize = request.json.get('endRow') - request.json.get('startRow')
    if results and len(results) > pageSize :
        return results[0:pageSize]
    else:
        return results
