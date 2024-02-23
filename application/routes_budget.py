import json
from datetime import datetime

from dateutil.relativedelta import relativedelta
from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, abort, make_response
from sqlalchemy import func, select, update, delete, text, insert, desc

from application import db
from application.models import Transactions, Category

bp = Blueprint('bp_budget', __name__)

@bp.route('/budget')
def budget():
    if form_date := request.form.get("start_date"):
        start_date = datetime.strptime(form_date, "%Y-%m")
    else:
        start_date = datetime.now()

    if form_date := request.form.get("end_date"):
        end_date = datetime.strptime(form_date, "%Y-%m")
    else:
        end_date = start_date + relativedelta(months=1)

    return render_template('budget.html', start_date=start_date.strftime("%Y-%m"), end_date=end_date.strftime("%Y-%m"))

@bp.route('/budget/data/<start_date>/<end_date>', methods=['GET'])
def get_account_data(start_date, end_date):
    start_date = datetime.strptime(start_date, "%Y-%m")
    end_date = datetime.strptime(end_date, "%Y-%m")

    entries = (
        db.session.execute(select(Transactions.category_id, Category.type, func.sum(Transactions.amount))
        .join(Category)
        .filter(
            Transactions.date >= start_date,
            Transactions.date < end_date,
        )
        .group_by(Transactions.category_id)
        .order_by(Category.type))
        .all()
    )
    budgets_list = [row.as_dict() for row in entries]

    category_data = Category.query.all()
    category_types = {category.type for category in category_data}

    category_list = {}
    for category_type in category_types:
        category_list[category_type] = {'type': category_type, 'children': []}

    for category in category_data:
        category_list[category.type]['children'].append({'name': category.name})

    return jsonify(budgets_list=budgets_list, category_list=list(category_list.values()))
