import json
from datetime import datetime

from dateutil.relativedelta import relativedelta
from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, abort, make_response
from sqlalchemy import func, select, text

from application import db
from application.form import TRANSACTION_CATEGORY, BulkDataForm, UserDataForm
from application.models import IncomeExpenses

bp = Blueprint('bp_dashboard', __name__)

@bp.route("/", methods=["GET", "POST"])
def dashboard():
    if form_date := request.form.get("start_date"):
        start_date = datetime.strptime(form_date, "%Y-%m")
    else:
        start_date = datetime.now()

    if form_date := request.form.get("end_date"):
        end_date = datetime.strptime(form_date, "%Y-%m")
    else:
        end_date = start_date + relativedelta(months=1)

    income_vs_expense = (
        db.session.execute(text(
            """SELECT credit.agg_date, credit.income, debit.expense
                    FROM
                        (SELECT strftime('%m-%Y', date) AS agg_date, SUM(amount) AS income
                        FROM income_expenses
                        WHERE category_id != 'Transfer' AND type == 'credit'
                        GROUP BY agg_date) AS credit,
                        (SELECT strftime('%m-%Y', date) AS agg_date, SUM(amount) AS expense
                        FROM income_expenses
                        WHERE category_id != 'Transfer' AND type == 'debit'
                        GROUP BY agg_date) AS debit
                    WHERE credit.agg_date == debit.agg_date
                """
            )).all()
    )


    category_comparison = (
        db.session.execute(select(IncomeExpenses.category_id, func.sum(IncomeExpenses.amount))
        .filter(
            IncomeExpenses.category_id != "Transfer",
            IncomeExpenses.type == "debit",
            IncomeExpenses.date >= start_date,
            IncomeExpenses.date < end_date,
        )
        .group_by(IncomeExpenses.category_id))
        .all()
    )

    dates = (
        db.session.execute(select(IncomeExpenses.date, func.sum(IncomeExpenses.amount))
        .filter(
            IncomeExpenses.category_id != "Transfer",
            IncomeExpenses.type == "debit",
            IncomeExpenses.date >= start_date,
            IncomeExpenses.date < end_date,
        )
        .group_by(IncomeExpenses.date))
        .all()
    )

    income_category_data = [{'category': row[0], 'total': float(row[1])} for row in category_comparison]
    income_expense_data = [{'date': row[0], 'income': float(row[1]), 'expense': float(row[2]*-1), 'total': float(row[1])-float(row[2])} for row in income_vs_expense]
    over_time_expenditure = [{'date': row[0].strftime("%m-%d-%y"), 'total': float(row[1])} for row in dates]

    return render_template(
        "dashboard.html",
        income_vs_expense_data=json.dumps(income_expense_data),
        income_category_data=json.dumps(income_category_data),
        over_time_expenditure=json.dumps(over_time_expenditure),
        start_date=start_date.strftime("%Y-%m"),
        end_date=end_date.strftime("%Y-%m"),
    )

@bp.route("/dashboard/data", methods=['GET', 'POST'])
def send_dashboard_data():
    data = request.get_json()
    start_date = datetime.strptime(data['start_date'], "%Y-%m")
    end_date = datetime.strptime(data['end_date'], "%Y-%m")

    income_vs_expense = (
        db.session.execute(text(
            """SELECT credit.agg_date, credit.income, debit.expense
                    FROM
                        (SELECT strftime('%m-%Y', date) AS agg_date, SUM(amount) AS income
                        FROM income_expenses
                        WHERE category_id != 'Transfer' AND type == 'credit'
                        GROUP BY agg_date) AS credit,
                        (SELECT strftime('%m-%Y', date) AS agg_date, SUM(amount) AS expense
                        FROM income_expenses
                        WHERE category_id != 'Transfer' AND type == 'debit'
                        GROUP BY agg_date) AS debit
                    WHERE credit.agg_date == debit.agg_date
                """
            )).all()
    )


    category_comparison = (
        db.session.execute(select(IncomeExpenses.category, func.sum(IncomeExpenses.amount))
        .filter(
            IncomeExpenses.category_id != "Transfer",
            IncomeExpenses.type == "debit",
            IncomeExpenses.date >= start_date,
            IncomeExpenses.date < end_date,
        )
        .group_by(IncomeExpenses.category))
        .all()
    )

    dates = (
        db.session.execute(select(IncomeExpenses.date, func.sum(IncomeExpenses.amount))
        .filter(
            IncomeExpenses.category_id != "Transfer",
            IncomeExpenses.type == "debit",
            IncomeExpenses.date >= start_date,
            IncomeExpenses.date < end_date,
        )
        .group_by(IncomeExpenses.date))
        .all()
    )

    income_category_data = [{'category': row[0], 'total': float(row[1])} for row in category_comparison]
    income_expense_data = [{'date': row[0], 'income': float(row[1]), 'expense': float(row[2]*-1), 'total': float(row[1])-float(row[2])} for row in income_vs_expense]
    over_time_expenditure = [{'date': row[0].strftime("%m-%d-%y"), 'total': float(row[1])} for row in dates]

    return make_response(jsonify(income_category_data=income_category_data, income_expense_data=income_expense_data, over_time_expenditure=over_time_expenditure), 200) # HTTP_200_OK


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        # bp.logger.error("No Content-Type specified.")
        abort(
            415, # HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    # bp.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        415, # HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
