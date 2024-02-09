import json
from datetime import datetime

from dateutil.relativedelta import relativedelta
from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, abort, make_response
from sqlalchemy import func, select, update, delete, text

from application import db
from application.form import TRANSACTION_CATEGORY, BulkDataForm, UserDataForm
from application.models import IncomeExpenses

bp = Blueprint('bp_transactions', __name__)

@bp.route("/transactions", methods=["GET", "POST"])
def transactions_view():
    if form_date := request.form.get("start_date"):
        start_date = datetime.strptime(form_date, "%Y-%m")
    else:
        start_date = datetime.now()

    if form_date := request.form.get("end_date"):
        end_date = datetime.strptime(form_date, "%Y-%m")
    else:
        end_date = start_date + relativedelta(months=1)

    entries = IncomeExpenses.query.filter(
        IncomeExpenses.date >= start_date,
        IncomeExpenses.date < end_date
    )
    return render_template(
        "transactions.html", entries=entries, categories=TRANSACTION_CATEGORY, start_date=start_date.strftime("%Y-%m"), end_date=end_date.strftime("%Y-%m")
    )

@bp.route('/update')
def update_row():
    new_data = json.loads(request.args.get('new_data'))
    db.session.execute(
        update(IncomeExpenses)
        .where(IncomeExpenses.id==new_data['index'])
        .values({
            "date": datetime.strptime(new_data['date'], "%Y-%m-%d"),
            "description":new_data['description'],
            "amount":new_data['amount'],
            "type":new_data['type'],
            "category":new_data['category'],
            "account":new_data['account'],
            "bank":new_data['bank']
        })
    )
    db.session.commit()
    return jsonify()

@bp.route('/data')
def get_table_data():
    if form_date := request.form.get("start_date"):
        start_date = datetime.strptime(form_date, "%Y-%m")
    else:
        start_date = datetime.now()

    if form_date := request.form.get("end_date"):
        end_date = datetime.strptime(form_date, "%Y-%m")
    else:
        end_date = start_date + relativedelta(months=1)

    entries = IncomeExpenses.query.filter(
        IncomeExpenses.date >= start_date,
        IncomeExpenses.date < end_date
    )
    return jsonify(entries=entries,
                   categories=TRANSACTION_CATEGORY,
                   start_date=start_date.strftime("%Y-%m"),
                   end_date=end_date.strftime("%Y-%m")
    )
