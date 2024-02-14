import json
from datetime import datetime

from dateutil.relativedelta import relativedelta
from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, abort, make_response
from sqlalchemy import func, select, update, delete, text, insert

from application import db
from application.models import Account

bp = Blueprint('bp_balances', __name__)

@bp.route('/balances')
def categories():
    return render_template('balances.html')

@bp.route('/account/data')
def get_account_data():
    account_data = Account.query.all()
    accounts_list = [row.as_dict() for row in account_data]
    return jsonify(accounts_list=accounts_list)

@bp.route('/account/update')
def update_row():
    new_data = json.loads(request.args.get('new_data'))

    db.session.execute(
        update(Account)
        .where(Account.id==new_data['id'])
        .values({
            Account.date: datetime.strptime(new_data['date'], "%a, %d %b %Y %H:%M:%S GMT"),
            Account.bank: new_data['bank'],
            Account.account: new_data['account'],
            Account.value: new_data['value'],
            Account.retirement: new_data['retirement'],
            Account.type: new_data['type'],
            Account.category: new_data['category'],
        })
    )
    db.session.commit()
    return get_account_data()


@bp.route('/account/delete/<int:entry_id>')
def delete_row(entry_id):
    entry = Account.query.get_or_404(int(entry_id))
    db.session.delete(entry)
    db.session.commit()
    flash("Entry deleted", "success")
    return get_account_data()
