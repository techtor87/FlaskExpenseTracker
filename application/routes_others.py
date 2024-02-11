import json
from datetime import datetime

from dateutil.relativedelta import relativedelta
from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, abort, make_response
from sqlalchemy import func, select, text

from application import db
from application.form import TRANSACTION_CATEGORY, BulkDataForm, UserDataForm
from application.models import IncomeExpenses

bp = Blueprint('bp', __name__)

@bp.route("/add", methods=["POST", "GET"])
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


@bp.route("/import", methods=["POST", "GET"])
def import_expense():
    form = BulkDataForm()
    if form.validate_on_submit():
        if '\t' in form.bulk_data.data:
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
        elif '"Date",' in form.bulk_data.data:
            for line in form.bulk_data.data.splitlines():
                data = line.split(",")
                if data != "" and '"Date"' not in data[0]:
                    data = [item.replace('"', '') for item in data]
                    entry = IncomeExpenses(
                        date=datetime.strptime(data[0], "%m/%d/%Y").date(),
                        description=data[1],
                        amount=data[3],
                        type=data[4],
                        category=data[5],
                        account=data[6],
                        bank=data[6],
                    )

        db.session.commit()
        flash(
            f"{len(form.bulk_data.data.splitlines())} entries has been added", "success"
        )
        return redirect(url_for("transactions_view"))
    return render_template("import.html", title="Import Transactions", form=form)


@bp.route("/delete-post/<int:entry_id>")
def delete(entry_id):
    entry = IncomeExpenses.query.get_or_404(int(entry_id))
    db.session.delete(entry)
    db.session.commit()
    flash("Entry deleted", "success")
    return redirect(url_for("transactions_view"))