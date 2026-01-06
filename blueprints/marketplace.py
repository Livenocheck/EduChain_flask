from flask import Blueprint, request, render_template, flash, redirect, session
from models import db
from models.user import User
from models.token_balance import TokenBalance
from models.reward import Reward
from models.transaction import Transaction
from functools import wraps

bp = Blueprint('marketplace', __name__, url_prefix='/marketplace')

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("❌ Сначала авторизуйтесь", "error")
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@student_required
def index():
    user = User.query.get(session['user_id'])
    balance_obj = TokenBalance.query.filter_by(user_id=user.id).first()
    rewards = Reward.query.filter_by(school_id=user.school_id).all()
    return render_template('marketplace.html', 
                         balance=balance_obj.balance if balance_obj else 0,
                         rewards=rewards)

@bp.route('/buy/<int:reward_id>', methods=['POST'])
@student_required
def buy_reward(reward_id):
    user = User.query.get(session['user_id'])
    reward = Reward.query.get(reward_id)
    
    if not reward or reward.school_id != user.school_id:
        flash("❌ Награда не найдена", "error")
        return redirect('/marketplace')
    
    balance_obj = TokenBalance.query.filter_by(user_id=user.id).first()
    if not balance_obj or balance_obj.balance < reward.cost:
        flash("❌ Недостаточно токенов", "error")
        return redirect('/marketplace')
    
    if reward.quantity is not None and reward.quantity <= 0:
        flash("❌ Награда закончилась", "error")
        return redirect('/marketplace')
    
    balance_obj.balance -= reward.cost
    if reward.quantity is not None:
        reward.quantity -= 1
    
    tx = Transaction(user_id=user.id, type='purchase', amount=reward.cost, 
                    description=f"Покупка: {reward.name}", reward_id=reward.id)
    db.session.add(tx)
    db.session.commit()
    
    flash(f"✅ Успешно! Новый баланс: {balance_obj.balance} 🪙", "success")
    return redirect('/marketplace')