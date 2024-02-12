from application import app
from application import db
from application.models import Category, IncomeExpenses, Account, Rules

with app.app_context():
    db.create_all()
