import json
from datetime import datetime

from dateutil.relativedelta import relativedelta
from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, abort, make_response
from sqlalchemy import func, select, update, delete, text, insert, desc

from application import db
from application.models import Account, Balance

bp = Blueprint('bp_balances', __name__, url_prefix='/account')

@bp.route('/balances')
def categories():
    return render_template('balances.html')

@bp.route('/data')
def get_account_data():
    account_data = Account.query.all()
    accounts_list = [row.as_dict() for row in account_data]
    for account in accounts_list:
        current_balance = Balance.query.where(Balance.bank_id == account['id']).order_by(Balance.date.desc()).first()
        account.update(
            {
                'value':float(current_balance.value) if current_balance else None
            }
        )
    return jsonify(accounts_list=accounts_list)

@bp.route('/update')
def update_row():
    new_data = json.loads(request.args.get('new_data'))

    db.session.execute(
        update(Account)
        .where(Account.id==new_data['id'])
        .values({
            Account.bank: new_data['bank'],
            Account.account: new_data['account'],
            Account.retirement: new_data['retirement'],
            Account.type: new_data['type'],
            Account.category: new_data['category'],
        })
    )
    db.session.commit()
    return get_account_data()


@bp.route('/delete/<int:entry_id>')
def delete_row(entry_id):
    entry = Account.query.get_or_404(int(entry_id))
    db.session.delete(entry)
    db.session.commit()
    flash("Entry deleted", "success")
    return get_account_data()
