# blueprints/web.py
from flask import Blueprint, request, render_template, redirect
from telegram_tools.telegram_auth import validate_init_data

bp = Blueprint('web', __name__)

@bp.route('/')
def index():
    init_data = request.args.get('initData')
    if init_data:
        # Пытаемся валидировать данные
        data = validate_init_data(init_data)
        if data and 'user' in data:
            # Ученик → Mini App
            return redirect(f"/tg_app/?initData={init_data}")
        else:
            # Битый initData → ошибка, НЕ показываем админку!
            return "Invalid Telegram data", 400
    
    # Только если НЕТ initData → показываем админку
    return render_template('index.html')
