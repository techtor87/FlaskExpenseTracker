from datetime import datetime

from application import db


class Category(db.Model):
    name = db.Column(db.String(30), primary_key=True)
    type = db.Column(db.String(30), nullable=False)
    transactions = db.relationship('Transactions', back_populates='category')

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Account(db.Model):
    id = db.Column(db.String(30), primary_key=True)
    bank = db.Column(db.String(30), nullable=False)
    account = db.Column(db.String(30), nullable=False)
    retirement = db.Column(db.Boolean, default=False)
    type = db.Column(db.String(30), nullable=True)
    category = db.Column(db.String(30), nullable=True)
    plaid_item_id = db.Column(db.String(30), nullable=True)
    balance = db.relationship('Balance', back_populates='bank')

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Balance(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    account_id = db.Column(db.String(30))
    date = db.Column(db.Date, default=datetime.now, nullable=False)
    bank_id = db.Column(db.ForeignKey(Account.id), nullable=False)
    bank = db.relationship("Account", back_populates='balance')
    value = db.Column(db.DECIMAL(10, 2), nullable=False)
    transactions = db.relationship('Transactions', back_populates='bank_account')

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Transactions(db.Model):
    id = db.Column(db.String(30), primary_key=True)
    date = db.Column(db.Date, default=datetime.now, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.DECIMAL(10, 2), nullable=False)
    type = db.Column(db.String(30), default="debit", nullable=False)
    category_id = db.Column(db.ForeignKey(Category.name), nullable=False)
    category = db.relationship("Category", back_populates='transactions')
    bank_account_id = db.Column(db.ForeignKey(Balance.account_id), nullable=False)
    bank_account = db.relationship('Balance', back_populates='transactions')

    def as_dict(self):
        def filter_func(pair):
            if pair[0].startswith('_'):
                return False
            if type(pair[1]) == Balance:
                return False
            return True
        return dict(filter(filter_func, vars(self).items()))

        # return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Rules(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    IF = db.Column(db.String(255), nullable=False)
    THEN = db.Column(db.String(255), nullable=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
