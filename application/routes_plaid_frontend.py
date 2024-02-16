from flask import Blueprint, request, jsonify, render_template

bp = Blueprint('bp_frontend', __name__)

@bp.route('/plaid')
def frontend():
    return render_template('plaid.html')
