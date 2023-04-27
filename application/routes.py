from application import app
from flask import render_template, url_for, redirect,flash, get_flashed_messages
from application.form import UserDataForm, BulkDataForm, TRANSACTION_CATEGORY
from application.models import IncomeExpenses, Account
from application import db
from datetime import datetime
import json

@app.route('/transactions')
def transactions_view():
    entries = IncomeExpenses.query
    return render_template('transactions.html', entries = entries, categories = TRANSACTION_CATEGORY)


@app.route('/add', methods = ["POST", "GET"])
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
        return redirect(url_for('transactions_view'))
    return render_template('add.html', title="Add Transactions", form=form)


@app.route('/import', methods = ["POST", "GET"])
def import_expense():
    form = BulkDataForm()
    if form.validate_on_submit():
        for line in form.bulk_data.data.splitlines():
            data = line.split('\t')
            if data != '':
                entry = IncomeExpenses(
                    date=datetime.strptime(data[0], '%m/%d/%Y').date(),
                    description=data[1],
                    amount=data[3],
                    type=data[4],
                    category=data[5],
                    account=data[6],
                    bank=data[6],
                )
                db.session.add(entry)
        db.session.commit()
        flash(f"{len(form.bulk_data.data.splitlines())} entries has been added", "success")
        return redirect(url_for('transactions_view'))
    return render_template('import.html', title="Import Transactions", form=form)

@app.route('/delete-post/<int:entry_id>')
def delete(entry_id):
    entry = IncomeExpenses.query.get_or_404(int(entry_id))
    db.session.delete(entry)
    db.session.commit()
    flash("Entry deleted", "success")
    return redirect(url_for("transactions_view"))


@app.route('/')
def dashboard():
    income_vs_expense = db.session.query(db.func.sum(IncomeExpenses.amount), IncomeExpenses.type).group_by(IncomeExpenses.type).order_by(IncomeExpenses.type).all()

    category_comparison = db.session.query(db.func.sum(IncomeExpenses.amount), IncomeExpenses.category).group_by(IncomeExpenses.category).order_by(IncomeExpenses.category).all()

    dates = db.session.query(db.func.sum(IncomeExpenses.amount), IncomeExpenses.date).group_by(IncomeExpenses.date).order_by(IncomeExpenses.date).all()

    income_category = []
    for amounts, _ in category_comparison:
        income_category.append(amounts)

    income_expense = []
    for total_amount, _ in income_vs_expense:
        income_expense.append(total_amount)

    over_time_expenditure = []
    dates_label = []
    for amount, date in dates:
        dates_label.append(date.strftime("%m-%d-%y"))
        over_time_expenditure.append(amount)

    return render_template('dashboard.html',
                            income_vs_expense=json.dumps(income_expense),
                            income_category=json.dumps(income_category),
                            over_time_expenditure=json.dumps(over_time_expenditure),
                            dates_label =json.dumps(dates_label)
                        )
