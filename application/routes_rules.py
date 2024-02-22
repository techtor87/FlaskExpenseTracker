import json
from datetime import datetime

from dateutil.relativedelta import relativedelta
from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, abort, make_response
from sqlalchemy import func, select, update, delete, text, insert

from application import db
from application.form import BulkDataForm, UserDataForm
from application.models import Transactions, Rules

bp = Blueprint('bp_rules', __name__)

@bp.route('/rules')
def categories():
    return render_template('category_management.html')#, category_list=category_list)

@bp.route('/rules/data')
def get_category_data():
    rules_list = [r.as_dict() for r in Rules.query.all()]
    return jsonify(rules_list=rules_list)

@bp.route('/rules/update')
def update_row():
    new_data = json.loads(request.args.get('new_data'))

    if new_data.get('id'):
        db.session.execute(
            update(Rules)
            .where(Rules.id==new_data['id'])
            .values({
                Rules.if_field: new_data['if_field'],
                Rules.if_operation: new_data['if_operation'],
                Rules.if_statement: new_data['if_statement'],
                Rules.then_field: new_data['then_field'],
                Rules.then_statement: new_data['then_statement'],
            })
        )
    else:
        db.session.add(Rules(
            if_field=new_data.get('if_field', '[empty]'),
            if_operation=new_data.get('if_operation', '[empty]'),
            if_statement=new_data.get('if_statement', '[empty]'),
            then_field=new_data.get('then_field', '[empty]'),
            then_statement=new_data.get('then_statement', '[empty]')))
    db.session.commit()
    return get_category_data()

@bp.route('/rules/delete')
def delete_row():
    remove_data = json.loads(request.args.get('delete_data'))
    for row in remove_data:
        entry = Rules.query.get_or_404(row['id'])
        db.session.delete(entry)
    db.session.commit()
    return get_category_data()
