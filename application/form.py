from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    DecimalField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired

TRANSACTION_CATEGORY = [
    # Income Groups
    ("Paycheck"),
    ("Interest Income"),
    ("Income"),
    # Fixed Needs Groups
    ("Mortage & Rent"),
    ("Natural Gas"),
    ("Water"),
    ("Internet"),
    ("Phone"),
    ("Trash"),
    ("Life Insurance"),
    ("Transfer to Tithe"),
    ("Auto Insurance"),
    # Variable Needs Groups
    ("Groceries"),
    ("Gas & Fuel"),
    ("Electric"),
    ("Tuition & Daycare"),
    ("Nec Expense"),
    ("Medical"),
    ("Tax"),
    ("Home Exp"),
    ("Auto & Transport"),
    ("Work Expense"),
    # Variable Wants Groups
    ("Netflix"),
    ("Eat Out - Both"),
    ("Eat Out - Greg"),
    ("Eat Out - Emily"),
    ("Cash & ATM"),
    ("Other"),
    ("Exercise"),
    ("Gift"),
    ("Shopping"),
    ("Home Improvement"),
    ("Television"),
    ("Vacation"),
    ("Clothing"),
    ("Entertainment"),
    ("Hobbies"),
    ("Cleaning Service"),
    ("Business Expense"),
    # Savings Groups
    ("Retirement IRA - Greg"),
    ("529 College Savings"),
    ("Savings"),
    ("Emergency"),
    ("Extra Mortgage & Rent"),
    # Rental Groups
    ("Kentwood Income"),
    ("Kentwood Mortgage"),
    ("Kentwood Expense"),
    ("29th Income"),
    ("29th Mortgage"),
    ("29th Expense"),
    ("Cranberry Income"),
    ("Cranberry Mortgage"),
    ("Cranberry Expense"),
    ("Chelsea Income"),
    ("Chelsea Mortgage"),
    ("Chelsea Expense"),
    ("Geist Income"),
    ("Geist Mortgage"),
    ("Geist Expense"),
]


class BulkDataForm(FlaskForm):
    bulk_data = TextAreaField("Data", validators=[DataRequired()])
    submit = SubmitField("Import Transactions")


class UserDataForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    amount = DecimalField("Amount", validators=[DataRequired()])
    type = SelectField(
        "Type",
        validators=[DataRequired()],
        choices=[("debit", "debit"), ("credit", "credit")],
    )
    category = SelectField("Category", choices=TRANSACTION_CATEGORY)
    account = StringField("Account Name", validators=[DataRequired()])
    bank = StringField("Account Name", validators=[DataRequired()])
    submit = SubmitField("Add Transaction")
