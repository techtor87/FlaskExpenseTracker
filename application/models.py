from datetime import datetime

from application import db


class IncomeExpenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.now, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.DECIMAL(10, 2), nullable=False)
    type = db.Column(db.String(30), default="debit", nullable=False)
    category = db.Column(db.String(30), nullable=False)
    account = db.Column(db.String(30), nullable=False)
    bank = db.Column(db.String(30), nullable=False)


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.now, nullable=False)
    bank = db.Column(db.String(30), nullable=False)
    account = db.Column(db.String(30), nullable=False)
    value = db.Column(db.DECIMAL(10, 2), nullable=False)
    retirement = db.Column(db.Boolean, default=False)
    retirement = db.Column(db.Boolean, default=False)
