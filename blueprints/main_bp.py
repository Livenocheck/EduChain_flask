from flask import Blueprint, request, render_template
from telegram_tools.telegram_auth import validate_init_data, get_or_create_student
import jwt
from models import db
from models.token_balance import TokenBalance

bp = Blueprint('main', __name__, url_prefix='/tg_app')

@bp.route('/')
def student_app():
    init_data = request.args.get('initData')
    if not init_data:
        return "Unauthorized", 403
    
    data = validate_init_data(init_data)
    if not data or 'user' not in data:
        return "Invalid initData", 403
    
    try:
        user_data = jwt.decode(data['user'], options={"verify_signature": False})
    except Exception:
        return "Invalid user data", 400
    
    user = get_or_create_student(user_data['id'], user_data.get('first_name', 'Аноним'))
    
    # Безопасное получение баланса
    balance_obj = TokenBalance.query.filter_by(user_id=user.id).first()
    if not balance_obj:
        balance_obj = TokenBalance(user_id=user.id, balance=0)
        db.session.add(balance_obj)
        db.session.commit()
    
    return render_template('app.html', student=user, balance=balance_obj.balance, init_data=init_data)