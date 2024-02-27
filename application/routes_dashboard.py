import json
from datetime import datetime

from dateutil.relativedelta import relativedelta
from flask import Blueprint, session, flash, redirect, render_template, request, url_for, jsonify, abort, make_response
from sqlalchemy import func, select, text

from application import db
from application.form import TRANSACTION_CATEGORY, BulkDataForm, UserDataForm
from application.models import Transactions, Category, Balance, Account

bp = Blueprint('bp_dashboard', __name__)

@bp.route("/", methods=["GET", "POST"])
def dashboard():
    if form_date := request.form.get("start_date"):
        session['start_date'] = form_date
    else:
        session['start_date'] = datetime.strftime(datetime.now(), "%Y-%m")

    if form_date := request.form.get("end_date"):
        session['end_date'] = form_date
    else:
        session['end_date'] = datetime.strftime(datetime.now() + relativedelta(months=1), "%Y-%m")


    return render_template(
        "dashboard.html"
    )

@bp.route("/dashboard/data", methods=['GET', 'POST'])
def send_dashboard_data():
    start_date = datetime.strptime(session['start_date'], "%Y-%m")
    end_date = datetime.strptime(session['end_date'], "%Y-%m")

    income_vs_expense = (
        db.session.execute(text(
            """SELECT credit.agg_date, credit.income, debit.expense
                    FROM
                        (SELECT strftime('%m-%Y', date) AS agg_date, SUM(amount) AS income
                        FROM transactions
                        WHERE category_id != 'Transfer' AND category_id != 'EXCLUDE' AND type == 'credit'
                        GROUP BY agg_date) AS credit,
                        (SELECT strftime('%m-%Y', date) AS agg_date, SUM(amount) AS expense
                        FROM transactions
                        WHERE category_id != 'Transfer' AND type == 'debit'
                        GROUP BY agg_date) AS debit
                    WHERE credit.agg_date == debit.agg_date
                """
            )).all()
    )


    category_comparison = (
        db.session.execute(select(Transactions.category_id, Category.type, func.sum(Transactions.amount))
        .join(Category)
        .filter(
            Transactions.category_id != "Transfer",
            Transactions.category_id != "EXCLUDE",
            Transactions.type == "debit",
            Transactions.date >= start_date,
            Transactions.date < end_date,
        )
        .group_by(Transactions.category_id)
        .order_by(Category.type))
        .all()
    )
    category_type_comparison = (
        db.session.execute(select(Category.type, func.sum(Transactions.amount))
        .join(Category)
        .filter(
            Transactions.category_id != "Transfer",
            Transactions.category_id != "EXCLUDE",
            Transactions.type == "debit",
            Transactions.date >= start_date,
            Transactions.date < end_date,
        )
        .group_by(Category.type)
        .order_by(Category.type))
        .all()
    )

    dates = (
        db.session.execute(select(Transactions.date, func.sum(Transactions.amount))
        .filter(
            Transactions.category_id != "Transfer",
            Transactions.category_id != "EXCLUDE",
            Transactions.type == "debit",
            Transactions.date >= start_date,
            Transactions.date < end_date,
        )
        .group_by(Transactions.date))
        .all()
    )

    date_balance = {}
    balance_dates = {}
    for account in Account.query.all():
        balances = Balance.query.where(Balance.bank_id == account.id).order_by(Balance.date).all()
        balance_dates[f'{account.bank}-{account.account}'] = []
        for balance_item in balances:
            balance_dates[f'{account.bank}-{account.account}'].append({
                # 'date': balance_item.date.strftime('%m-%d-%Y'),
                'date': balance_item.date,
                'value': float(balance_item.value)
            })

    expense_category_data = {'category': [{'category': row[0], 'category_type': row[1], 'total': float(row[2])} for row in category_comparison],
        'category_type': [{'type': row[0], 'total': float(row[1])} for row in category_type_comparison],
    }
    income_expense_data = [{'date': row[0], 'income': row[1]*-1, 'expense': row[2]*-1, 'total': ((row[1]*-1)+(row[2]*-1))} for row in income_vs_expense]
    over_time_expenditure = [{'date': row[0].strftime("%m-%d-%y"), 'total': float(row[1])} for row in dates]

    return make_response(jsonify(expense_category_data=expense_category_data,
                                 income_expense_data=income_expense_data,
                                 over_time_expenditure=over_time_expenditure,
                                 net_worth_data=balance_dates),
                         200) # HTTP_200_OK
