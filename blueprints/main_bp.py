from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for, flash
from functools import wraps
from telegram_tools.telegram_auth import validate_init_data, get_or_create_student
import json
from models import db
from models.user import User
from models.token_balance import TokenBalance
from models.transaction import Transaction
from models.reward import Reward

bp = Blueprint('main', __name__, url_prefix='/')

# Декоратор защиты для учеников
def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
def student_app():
    if 'user_id' not in session:
        return render_template('app.html', authorized=False, student=None)
    user = User.query.get(session['user_id'])
    if not user.verified and not user.verification_requested:
        return redirect('/profile')
    balance_obj = TokenBalance.query.filter_by(user_id=user.id).first()
    balance = balance_obj.balance if balance_obj else 0
    return render_template('app.html', authorized=True, student=user, balance=balance)

@bp.route('/auth', methods=['POST'])
def auth_student():
    init_data = request.json.get('initData')
    if not init_data:
        return jsonify({"valid": False, "error": "No auth data"}), 400
    
    data = validate_init_data(init_data)
    if not data or 'user' not in data:
        return jsonify({"valid": False, "error": "Invalid auth"}), 400
    
    try:
        user_data = json.loads(data['user'])
        user = get_or_create_student(user_data['id'], user_data.get('first_name', 'Аноним'))
        balance_obj = TokenBalance.query.filter_by(user_id=user.id).first()
        if not balance_obj:
            balance_obj = TokenBalance(user_id=user.id, balance=0)
            db.session.add(balance_obj)
            db.session.commit()
        
        session['user_id'] = user.id
        return jsonify({
            "valid": True,
            "student": {"id": user.id, "name": user.name},
            "balance": balance_obj.balance
        })
    except Exception as e:
        print(f"❌ AUTH ERROR DETAILS: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"valid": False, "error": "Auth failed"}), 500
    
@bp.route('/profile', methods=['GET', 'POST'])
@student_required
def profile():
    user = User.query.get(session['user_id'])
    if user.verified:
        return redirect('/')
    
    if request.method == 'POST':
        user.first_name = request.form['first_name'].strip()
        user.last_name = request.form['last_name'].strip()
        user.grade = request.form['grade'].strip()
        user.school_code = request.form.get('school_code', '').strip()
        user.verification_requested = True
        user.verification_rejected = False  # ← сбросить статус отклонения
        user.rejection_reason = None
        db.session.commit()
        flash("✅ Данные отправлены на повторную верификацию!", "success")
        return redirect('/')
    
    return render_template('profile.html', user=user)

@bp.route('/inventory')
@student_required
def inventory():
    user = User.query.get(session['user_id'])
    
    from sqlalchemy import func
    purchased_rewards = db.session.query(
        Transaction.reward_id,
        Reward.name,
        Reward.image_filename,
        func.count(Transaction.reward_id).label('quantity')
    ).join(Reward, Transaction.reward_id == Reward.id)\
     .filter(Transaction.user_id == user.id, Transaction.type == 'purchase')\
     .group_by(Transaction.reward_id, Reward.name, Reward.image_filename)\
     .all()
    
    balance_obj = TokenBalance.query.filter_by(user_id=user.id).first()
    balance = balance_obj.balance if balance_obj else 0
    
    return render_template(
        'inventory.html',
        student=user,
        balance=balance,
        rewards=purchased_rewards  # Список: (reward_id, name, image_url, quantity)
    )

@bp.route('/history')
@student_required
def purchase_history():
    user = User.query.get(session['user_id'])
    purchases = Transaction.query\
        .filter_by(user_id=user.id, type='purchase')\
        .order_by(Transaction.timestamp.desc())\
        .all()
    rewards = {p.reward_id: Reward.query.get(p.reward_id) for p in purchases}
    
    balance_obj = TokenBalance.query.filter_by(user_id=user.id).first()
    balance = balance_obj.balance if balance_obj else 0
    
    return render_template('history.html', student=user, balance=balance, purchases=purchases, rewards=rewards)
