from flask import Blueprint, request, render_template, jsonify, redirect
from telegram_tools.telegram_auth import validate_init_data, get_or_create_student
import json
from models import db
from models.user import User
from models.token_balance import TokenBalance
from models.reward import Reward
from models.transaction import Transaction

bp = Blueprint('marketplace', __name__, url_prefix='/marketplace')

@bp.route('/')
def index():
    # Только HTML — данные загружаются через AJAX
    return render_template('marketplace.html')

@bp.route('/load', methods=['POST'])
def load_marketplace():
    init_data = request.json.get('initData')
    if not init_data:
        return jsonify({"valid": False, "error": "No auth"}), 400
    
    data = validate_init_data(init_data)
    if not data or 'user' not in data:
        return jsonify({"valid": False, "error": "Invalid auth"}), 400
    
    user_data = json.loads(data['user'])
    user = get_or_create_student(user_data['id'], user_data.get('first_name', 'Аноним'))
    balance_obj = TokenBalance.query.filter_by(user_id=user.id).first()
    rewards = Reward.query.filter_by(school_id=user.school_id).all()
    
    return jsonify({
        "valid": True,
        "balance": balance_obj.balance if balance_obj else 0,
        "rewards": [{
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "cost": r.cost,
            "quantity": r.quantity
        } for r in rewards]
    })

@bp.route('/buy/<int:reward_id>', methods=['POST'])
def buy_reward(reward_id):
    init_data = request.form.get('initData')
    if not init_data:
        return '''
        <!DOCTYPE html><html><body>
            <script src="https://telegram.org/js/telegram-web-app.js"></script>
            <script>Telegram.WebApp.showAlert("Ошибка: не авторизован"); setTimeout(() => window.location.href="/tg_app/", 1500);</script>
        </body></html>
        '''
    
    data = validate_init_data(init_data)
    if not data or 'user' not in data:
        return '''
        <!DOCTYPE html><html><body>
            <script src="https://telegram.org/js/telegram-web-app.js"></script>
            <script>Telegram.WebApp.showAlert("Ошибка: недействительные данные"); setTimeout(() => window.location.href="/tg_app/", 1500);</script>
        </body></html>
        '''
    
    user_data = json.loads(data['user'])
    user = get_or_create_student(user_data['id'], user_data.get('first_name', 'Аноним'))
    reward = Reward.query.get(reward_id)
    
    if not reward or reward.school_id != user.school_id:
        return '''
        <!DOCTYPE html><html><body>
            <script src="https://telegram.org/js/telegram-web-app.js"></script>
            <script>Telegram.WebApp.showAlert("Ошибка: награда не найдена"); setTimeout(() => window.location.href="/tg_app/", 1500);</script>
        </body></html>
        '''
    
    balance_obj = TokenBalance.query.filter_by(user_id=user.id).first()
    if not balance_obj or balance_obj.balance < reward.cost:
        return '''
        <!DOCTYPE html><html><body>
            <script src="https://telegram.org/js/telegram-web-app.js"></script>
            <script>Telegram.WebApp.showAlert("Ошибка: недостаточно токенов"); setTimeout(() => window.location.href="/tg_app/", 1500);</script>
        </body></html>
        '''
    if reward.quantity is not None and reward.quantity <= 0:
        return '''
        <!DOCTYPE html><html><body>
            <script src="https://telegram.org/js/telegram-web-app.js"></script>
            <script>Telegram.WebApp.showAlert("Ошибка: награда закончилась"); setTimeout(() => window.location.href="/tg_app/", 1500);</script>
        </body></html>
        '''
    
    balance_obj.balance -= reward.cost
    if reward.quantity is not None:
        reward.quantity -= 1
    
    tx = Transaction(
        user_id=user.id,
        type='purchase',
        amount=reward.cost,
        description=f"Покупка: {reward.name}",
        reward_id=reward.id
    )
    db.session.add(tx)
    db.session.commit()
    
    return redirect(f"/?initData={init_data}")
