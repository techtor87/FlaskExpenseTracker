import json
from datetime import datetime

from dateutil.relativedelta import relativedelta
from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, abort, make_response
from sqlalchemy import func, select, update, delete, text, insert

from application import db
from application.form import BulkDataForm, UserDataForm
from application.models import Transactions, Category

bp = Blueprint('bp_categories', __name__)

@bp.route('/categories')
def categories():
    category_list = [{'name': (r._asdict())['name'], 'type': (r._asdict())['type']} for r in db.session.execute(
        select(Category.name, Category.type)
        ).all()]
    return render_template('category_management.html')#, category_list=category_list)

@bp.route('/category/data')
def get_category_data():
    category_list = [{'name': (r._asdict())['name'], 'type': (r._asdict())['type']} for r in db.session.execute(
        select(Category.name, Category.type)
        ).all()]
    return jsonify(category_list=category_list)

@bp.route('/category/update')
def update_row():
    colId = request.args.get('colId')
    old_value = request.args.get('old_value')
    new_data = json.loads(request.args.get('new_data'))

    if old_value != None:
        db.session.execute(
            update(Category)
            .where(Category.name==(old_value if colId == 'name' else new_data['name']))
            .values({
                Category.name: new_data['name'],
                Category.type: new_data['type'],
            })
        )
    else:
        db.session.add(Category(name=new_data.get('name', '[empty]'), type=new_data.get('type', '[empty]')))
    db.session.commit()
    return get_category_data()

@bp.route('/category/delete')
def delete_row():
    remove_data = json.loads(request.args.get('delete_data'))
    for row in remove_data:
        entry = Category.query.get_or_404(row['name'])
        db.session.delete(entry)
    db.session.commit()
    return get_category_data()
