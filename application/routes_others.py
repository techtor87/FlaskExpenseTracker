import json
import random
import csv
from datetime import datetime

from dateutil.relativedelta import relativedelta
from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, abort, make_response
from sqlalchemy import func, select, text

from application import db
from application.form import BulkDataForm, UserDataForm
from application.models import Transactions, Category, Rules
from application.plaid_functions import apply_rule

bp = Blueprint('bp', __name__)

@bp.route("/add", methods=["POST", "GET"])
def add_expense():
    form = UserDataForm()
    if form.validate_on_submit():
        entry = Transactions(
            id=random.random() * 10000,
            date=form.date.data,
            description=form.description.data,
            amount=form.amount.data,
            type=form.type.data,
            category_id=form.category.data,
            bank_account_id=form.account.data,
        )

        db.session.add(entry)
        db.session.commit()
        flash(f"{form.type.data} has been added to {form.type.data}s", "success")
        return redirect(url_for("bp_transactions.transactions_view"))
    return render_template("add_transaction.html", title="Add Transactions", form=form)


@bp.route("/import", methods=["POST", "GET"])
def import_expense():
    form = BulkDataForm()
    if form.validate_on_submit():
        if 'rules_list' not in locals():
            rules_list = Rules.query.all()

        for data in csv.reader(form.bulk_data.data.splitlines(), delimiter='\t' if '\t' in form.bulk_data.data else ','):
            if data != "" and "Date" not in data[0]:
                entry = Transactions(
                    id=random.random()*10000,
                    date=datetime.strptime(data[0], "%m/%d/%Y").date(),
                    description=data[1],
                    amount=data[3],
                    type=data[4],
                    category_id=data[5],
                    bank_account_id=data[6],
                )
                for rule in rules_list:
                    entry = apply_rule(rule, entry)
                db.session.add(entry)

        flash(
            f"{len(db.session.new)} entries has been added", "success"
        )
        db.session.commit()
        return redirect(url_for("bp_transactions.transactions_view"))
    return render_template("import.html", title="Import Transactions", form=form)


@bp.route("/delete-post/<int:entry_id>")
def delete(entry_id):
    entry = Transactions.query.get_or_404(int(entry_id))
    db.session.delete(entry)
    db.session.commit()
    flash("Entry deleted", "success")
    return redirect(url_for("bp_transactions.transactions_view"))
