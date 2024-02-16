import datetime

from application import app, db
from application.models import Account, Balance, Category, Transactions, Rules
from application.routes_plaid import get_accounts, get_balance, get_holdings, get_transactions, get_assets
from sqlalchemy import func, select, update, delete, text, desc

def get_all_transactions():
    all_accounts = Account.query.all()
    for account in all_accounts:
        temp = get_transactions(account.plaid_item_id)

    return

def get_all_balances():
    all_accounts = Account.query.all()
    for account in all_accounts:
        balance_data = get_balance(account.plaid_item_id)
        for account_data in balance_data.json['accounts']:
            new_balance = Balance(
                date = datetime.datetime.today().date(),
                bank_id = account_data['persistent_account_id'],
                value = account_data['balances']['current'])
            old_balance = Balance.query.filter_by(bank_id = account_data['persistent_account_id']).order_by(Balance.date.desc()).first()
            if new_balance.date != old_balance.date or new_balance.value != old_balance.value:
                db.session.add(new_balance)

    db.session.commit()
    return

def get_all_assets():
    all_accounts = Account.query.all()
    for account in all_accounts:
        temp = get_assets(account.plaid_item_id)

    return

def get_all_holdings():
    all_accounts = Account.query.all()
    for account in all_accounts:
        temp = get_holdings(account.plaid_item_id)

    return
