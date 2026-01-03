from flask import Blueprint, request, render_template
from telegram_tools.telegram_auth import validate_init_data, get_or_create_student
import jwt
from models import db
from models.user import User
from models.token_balance import TokenBalance
from models.reward import Reward
from models.transaction import Transaction

bp = Blueprint('marketplace', __name__, url_prefix='/marketplace')

def show_alert_page(message, init_data, redirect_url="/tg_app/"):
    """Генерирует HTML-страницу с уведомлением и редиректом"""
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
    </head>
    <body>
        <script>
            Telegram.WebApp.ready();
            Telegram.WebApp.showAlert("{message}");
            setTimeout(() => {{
                window.location.href = "{redirect_url}?initData={init_data}";
            }}, 1500);
        </script>
    </body>
    </html>
    '''

@bp.route('/')
def index():
    """Основная страница маркета"""
    init_data = request.form.get('initData')
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
    balance_obj = TokenBalance.query.filter_by(user_id=user.id).first()
    if not balance_obj:
        balance_obj = TokenBalance(user_id=user.id, balance=0)
        db.session.add(balance_obj)
        db.session.commit()
    
    rewards = Reward.query.filter_by(school_id=user.school_id).all()
    return render_template('marketplace.html', 
                         student=user, 
                         balance=balance_obj.balance, 
                         rewards=rewards, 
                         init_data=init_data)

@bp.route('/buy/<int:reward_id>', methods=['POST'])
def buy_reward(reward_id):
    """Покупка награды (возвращает HTML-страницу с уведомлением)"""
    init_data = request.json.get('initData')
    if not init_data:
        return show_alert_page("Ошибка: не авторизован", "", "/tg_app/")
    
    data = validate_init_data(init_data)
    if not data or 'user' not in data:
        return show_alert_page("Ошибка: недействительные данные", "", "/tg_app/")
    
    try:
        user_data = jwt.decode(data['user'], options={"verify_signature": False})
    except Exception:
        return show_alert_page("Ошибка: битые данные пользователя", "", "/tg_app/")
    
    user = get_or_create_student(user_data['id'], user_data.get('first_name', 'Аноним'))
    reward = Reward.query.get(reward_id)
    
    if not reward or reward.school_id != user.school_id:
        return show_alert_page("Ошибка: награда не найдена", init_data)
    
    balance_obj = TokenBalance.query.filter_by(user_id=user.id).first()
    if not balance_obj:
        balance_obj = TokenBalance(user_id=user.id, balance=0)
        db.session.add(balance_obj)
        db.session.commit()
    
    if balance_obj.balance < reward.cost:
        return show_alert_page("Ошибка: недостаточно токенов", init_data)
    if reward.quantity is not None and reward.quantity <= 0:
        return show_alert_page("Ошибка: награда закончилась", init_data)
    
    # Списание токенов
    balance_obj.balance -= reward.cost
    if reward.quantity is not None:
        reward.quantity -= 1
    
    # Запись транзакции
    tx = Transaction(
        user_id=user.id,
        type='purchase',
        amount=reward.cost,
        description=f"Покупка: {reward.name}",
        reward_id=reward.id
    )
    db.session.add(tx)
    db.session.commit()
    
    return show_alert_page(f"Успешно! Новый баланс: {balance_obj.balance} 🪙", init_data)