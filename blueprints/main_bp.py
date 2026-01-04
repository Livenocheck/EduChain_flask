from flask import Blueprint, request, jsonify, render_template
from telegram_tools.telegram_auth import validate_init_data, get_or_create_student
import jwt
from models import db
from models.token_balance import TokenBalance

bp = Blueprint('main', __name__, url_prefix='/tg_app')

@bp.route('/')
def student_app():
    # Только HTML — без авторизации
    return render_template('app.html')

@bp.route('/auth', methods=['POST'])
def auth_student():
    """AJAX-авторизация ученика"""
    if request.is_json:
        init_data = request.json.get('initData')
    else:
        init_data = request.form.get('initData')
    
    if not init_data:
        return jsonify({"valid": False, "error": "No auth data"}), 400
    
    data = validate_init_data(init_data)
    if not data or 'user' not in data:
        return jsonify({"valid": False, "error": "Invalid auth"}), 400
    
    try:
        user_data = jwt.decode(data['user'], options={"verify_signature": False})
        user = get_or_create_student(user_data['id'], user_data.get('first_name', 'Аноним'))
        balance_obj = TokenBalance.query.filter_by(user_id=user.id).first()
        if not balance_obj:
            balance_obj = TokenBalance(user_id=user.id, balance=0)
            db.session.add(balance_obj)
            db.session.commit()
        
        return jsonify({
            "valid": True,
            "student": {"id": user.id, "name": user.name},
            "balance": balance_obj.balance,
            "initData": init_data
        })
    except Exception as e:
        return jsonify({"valid": False, "error": "Auth failed"}), 500