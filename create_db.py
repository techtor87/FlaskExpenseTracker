from application import app
from application import db
from application.models import IncomeExpenses, Account

with app.app_context():
    db.create_all()
