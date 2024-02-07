import json
from datetime import datetime

from dateutil.relativedelta import relativedelta
from flask import flash, redirect, render_template, request, url_for, jsonify
from sqlalchemy import func

from application import app, db
from application.form import TRANSACTION_CATEGORY, BulkDataForm, UserDataForm
from application.models import IncomeExpenses


@app.route("/transactions", methods=["GET", "POST"])
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


@app.route("/add", methods=["POST", "GET"])
def add_expense():
    form = UserDataForm()
    if form.validate_on_submit():
        entry = IncomeExpenses(
            date=form.date.data,
            description=form.description.data,
            amount=form.amount.data,
            type=form.type.data,
            category=form.category.data,
            account=form.account.data,
            bank=form.bank.data,
        )

        db.session.add(entry)
        db.session.commit()
        flash(f"{form.type.data} has been added to {form.type.data}s", "success")
        return redirect(url_for("transactions_view"))
    return render_template("add.html", title="Add Transactions", form=form)


@app.route("/import", methods=["POST", "GET"])
def import_expense():
    form = BulkDataForm()
    if form.validate_on_submit():
        for line in form.bulk_data.data.splitlines():
            data = line.split("\t")
            if data != "" and "Date" not in data[0]:
                entry = IncomeExpenses(
                    date=datetime.strptime(data[0], "%m/%d/%Y").date(),
                    description=data[1],
                    amount=data[3],
                    type=data[4],
                    category=data[5],
                    account=data[6],
                    bank=data[6],
                )
                db.session.add(entry)
        db.session.commit()
        flash(
            f"{len(form.bulk_data.data.splitlines())} entries has been added", "success"
        )
        return redirect(url_for("transactions_view"))
    return render_template("import.html", title="Import Transactions", form=form)


@app.route("/delete-post/<int:entry_id>")
def delete(entry_id):
    entry = IncomeExpenses.query.get_or_404(int(entry_id))
    db.session.delete(entry)
    db.session.commit()
    flash("Entry deleted", "success")
    return redirect(url_for("transactions_view"))


@app.route("/", methods=["GET", "POST"])
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
        db.session.query(IncomeExpenses.type, func.sum(IncomeExpenses.amount))
        .filter(IncomeExpenses.date >= start_date,
                IncomeExpenses.date < end_date)
        .group_by(IncomeExpenses.type)
        .all()
    )


    category_comparison = (
        db.session.query(IncomeExpenses.category, func.sum(IncomeExpenses.amount))
        .filter(
            IncomeExpenses.category != "Transfer",
            IncomeExpenses.type == "debit",
            IncomeExpenses.date >= start_date,
            IncomeExpenses.date < end_date,
        )
        .group_by(IncomeExpenses.category)
        .all()
    )

    dates = (
        db.session.query(IncomeExpenses.date, func.sum(IncomeExpenses.amount))
        .filter(
            IncomeExpenses.category != "Transfer",
            IncomeExpenses.type == "debit",
            IncomeExpenses.date >= start_date,
            IncomeExpenses.date < end_date,
        )
        .group_by(IncomeExpenses.date)
        .all()
    )

    income_category_labels = [row[0] for row in category_comparison]
    income_category_data = [float(row[1]) for row in category_comparison]

    income_expense_labels = [row[0] for row in income_vs_expense]
    income_expense_data = [{'type': row[0], 'total': float(row[1])} for row in income_vs_expense]

    over_time_expenditure = []
    dates_label = []
    for date, amount in dates:
        dates_label.append(date.strftime("%m-%d-%y"))
        over_time_expenditure.append(float(amount))

    return render_template(
        "dashboard.html",
        income_vs_expense_labels=json.dumps(income_expense_labels),
        income_vs_expense_data=json.dumps(income_expense_data),
        income_category_labels=json.dumps(income_category_labels),
        income_category_data=json.dumps(income_category_data),
        over_time_expenditure=json.dumps(over_time_expenditure),
        dates_label=json.dumps(dates_label),
        start_date=start_date.strftime("%Y-%m"),
        end_date=end_date.strftime("%Y-%m"),
    )
