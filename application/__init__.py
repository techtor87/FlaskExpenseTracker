from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import os
from dotenv import load_dotenv

import plaid
from plaid.model.products import Products
from plaid.api import plaid_api

from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = "JLKJJJO3IURYoiouolnojojouuoo=5y9y9youjuy952oohhbafdnoglhoho"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transactions.db'
app.config['DEBUG'] = True

db = SQLAlchemy(app)

# IMPORT MODELS AFTER CREATING SQLALCHEMY.DB BUT BEFORE CREATING THE DATABASE
from application.models import Category, Transactions, Account, Rules
with app.app_context():
    db.create_all()


# Fill in your Plaid API keys - https://dashboard.plaid.com/account/keys
PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
# Use 'sandbox' to test with Plaid's Sandbox environment (username: user_good,
# password: pass_good)
# Use `development` to test with live users and credentials and `production`
# to go live
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
# PLAID_PRODUCTS is a comma-separated list of products to use when initializing
# Link. Note that this list must contain 'assets' in order for the app to be
# able to create and retrieve asset reports.
PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'transactions').split(',')

# PLAID_COUNTRY_CODES is a comma-separated list of countries for which users
# will be able to select institutions from.
PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES', 'US').split(',')

host = plaid.Environment.Sandbox

if PLAID_ENV == 'sandbox':
    host = plaid.Environment.Sandbox

if PLAID_ENV == 'development':
    host = plaid.Environment.Development

if PLAID_ENV == 'production':
    host = plaid.Environment.Production

if (access_token := os.getenv('PLAID_ACCESS_TOKEN')) == '':
   access_token = None

def empty_to_none(field):
    value = os.getenv(field)
    if value is None or len(value) == 0:
        return None
    return value

PLAID_REDIRECT_URI = empty_to_none('PLAID_REDIRECT_URI')

configuration = plaid.Configuration(
    host=host,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
        'plaidVersion': '2020-09-14'
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

products = []
for product in PLAID_PRODUCTS:
    products.append(Products(product))


# We store the access_token in memory - in production, store it in a secure
# persistent data store.
access_token = None
# The payment_id is only relevant for the UK Payment Initiation product.
# We store the payment_id in memory - in production, store it in a secure
# persistent data store.
payment_id = None
# The transfer_id is only relevant for Transfer ACH product.
# We store the transfer_id in memory - in production, store it in a secure
# persistent data store.
transfer_id = None

item_id = None

from application.routes_others import bp as bp_other
from application.routes_dashboard import bp as bp_dashboard
from application.routes_transactions import bp as bp_transaction
from application.routes_plaid import bp as bp_plaid
from application.routes_plaid_frontend import bp as bp_frontend
from application.routes_category import bp as bp_category
from application.routes_balances import bp as bp_balance
app.register_blueprint(bp_other)
app.register_blueprint(bp_dashboard)
app.register_blueprint(bp_transaction)
app.register_blueprint(bp_plaid)
app.register_blueprint(bp_frontend)
app.register_blueprint(bp_category)
app.register_blueprint(bp_balance)


from sqlalchemy import func, select, update, delete, text
from application.models import Category
import plaid

TRANSACTION_CATEGORY = [
    ("EXCLUDE", "EXCLUDE"),
    # Income Groups
    ("Paycheck", 'Income'),
    ("Interest Income", 'Income'),
    ("Other Income", 'Income'),
    # Fixed Needs Groups
    ("Mortage & Rent", 'Fixed Needs'),
    ("Natural Gas", 'Fixed Needs'),
    ("Water", 'Fixed Needs'),
    ("Internet", 'Fixed Needs'),
    ("Phone", 'Fixed Needs'),
    ("Trash", 'Fixed Needs'),
    ("Life Insurance", 'Fixed Needs'),
    ("Transfer to Tithe", 'Fixed Needs'),
    ("Auto Insurance", 'Fixed Needs'),
    # Variable Needs Groups
    ("Groceries", 'Variable Needs'),
    ("Gas & Fuel", 'Variable Needs'),
    ("Electric", 'Variable Needs'),
    ("Tuition & Daycare", 'Variable Needs'),
    ("Nec Expense", 'Variable Needs'),
    ("Medical", 'Variable Needs'),
    ("Tax", 'Variable Needs'),
    ("Home Exp", 'Variable Needs'),
    ("Auto & Transport", 'Variable Needs'),
    ("Work Expense", 'Variable Needs'),
    # Variable Wants Groups
    ("Netflix", 'Variable Wants'),
    ("Eat Out - Both", 'Variable Wants'),
    ("Eat Out - Greg", 'Variable Wants'),
    ("Eat Out - Emily", 'Variable Wants'),
    ("Cash & ATM", 'Variable Wants'),
    ("Other", 'Variable Wants'),
    ("Exercise", 'Variable Wants'),
    ("Gift", 'Variable Wants'),
    ("Shopping", 'Variable Wants'),
    ("Home Improvement", 'Variable Wants'),
    ("Television", 'Variable Wants'),
    ("Vacation", 'Variable Wants'),
    ("Clothing", 'Variable Wants'),
    ("Entertainment", 'Variable Wants'),
    ("Hobbies", 'Variable Wants'),
    ("Cleaning Service", 'Variable Wants'),
    ("Business Expense", 'Variable Wants'),
    # Savings Groups
    ("Retirement IRA - Greg", 'Savings'),
    ("529 College Savings", 'Savings'),
    ("Savings", 'Savings'),
    ("Emergency", 'Savings'),
    ("Extra Mortgage & Rent", 'Savings'),
    # Rental Groups
    ("Kentwood Income", 'Business'),
    ("Kentwood Mortgage", 'Business'),
    ("Kentwood Expense", 'Business'),
    ("29th Income", 'Business'),
    ("29th Mortgage", 'Business'),
    ("29th Expense", 'Business'),
    ("Cranberry Income", 'Business'),
    ("Cranberry Mortgage", 'Business'),
    ("Cranberry Expense", 'Business'),
    ("Chelsea Income", 'Business'),
    ("Chelsea Mortgage", 'Business'),
    ("Chelsea Expense", 'Business'),
    ("Geist Income", 'Business'),
    ("Geist Mortgage", 'Business'),
    ("Geist Expense", 'Business'),
    ("Maple Income", 'Business'),
    ("Maple Mortgage", 'Business'),
    ("Maple Expense", 'Business'),
]

def fill_category_table():
    if len(db.session.execute(select(Category)).all()) == 0:
        for category, type in TRANSACTION_CATEGORY:
            db.session.add(Category(name=category, type=type))

        db.session.commit()

with app.app_context():
    fill_category_table()   # checks if cateogry table is filled and fills it if it's empty

import application.plaid_functions as plaid_functions


def initialize_requests():
    return

def update_plaid_data():
    # print('reoccuring task')
    with app.app_context():
        # plaid_functions.get_all_transactions()
        plaid_functions.get_all_balances()
        # plaid_functions.get_all_assets()
        # plaid_functions.get_all_holdings()
    return

scheduler = BackgroundScheduler()
initialize_requests()
job = scheduler.add_job(update_plaid_data, 'interval', minutes=1)
scheduler.start()
