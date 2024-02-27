import json
from datetime import datetime

from dateutil.relativedelta import relativedelta
from flask import session, Blueprint, flash, redirect, render_template, request, url_for, jsonify, abort, make_response
from sqlalchemy import func, select, update, delete, text, insert, desc

from application import db
from application.models import Transactions, Category

bp = Blueprint('bp_budget', __name__)

@bp.route('/budget', methods=['GET', 'POST'])
def budget():
    if form_date := request.form.get("start_date"):
        session['start_date'] = form_date
    else:
        session['start_date'] = datetime.strftime(datetime.now(), "%Y-%m")

    if form_date := request.form.get("end_date"):
        session['end_date'] = form_date
    else:
        session['end_date'] = datetime.strftime(datetime.now() + relativedelta(months=1), "%Y-%m")

    return render_template('budget.html')

@bp.route('/budget/data', methods=['GET', 'POST'])
def get_account_data():
    start_date = datetime.strptime(session['start_date'], "%Y-%m")
    end_date = datetime.strptime(session['end_date'], "%Y-%m")

    entries = (
        db.session.execute(
            select(text('strftime("%m-%Y", `date`)'), Transactions.category_id, func.sum(Transactions.amount))
        .join(Category)
        .filter(
            Transactions.date >= start_date,
            Transactions.date < end_date,
        )
        .group_by(Transactions.category_id)
        .order_by(Category.type))
        .all()
    )
    budgets_list = [row._asdict() for row in entries]

    category_data = Category.query.all()
    category_types = {category.type for category in category_data}

    category_list = {}
    for category_type in category_types:
        category_list[category_type] = {'type': category_type, 'children': []}

    for category in category_data:
        category_list[category.type]['children'].append({'name': category.name})

    return jsonify(budgets_list=budgets_list, category_list=list(category_list.values()))
