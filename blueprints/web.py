from flask import Blueprint, request, render_template, redirect
from telegram_tools.telegram_auth import validate_init_data, get_or_create_student
import jwt

bp = Blueprint('web', __name__)

@bp.route('/')
def index():
    init_data = request.args.get('initData')
    if init_data:
        data = validate_init_data(init_data)
        if data and 'user' in data:
            return redirect(f"/tg_app/?initData={init_data}")
        else:
            return "Invalid Telegram data", 400  # ← КРИТИЧЕСКИ ВАЖНО!
    return render_template('index.html')

@bp.route('/debug')
def debug():
    init_data = request.args.get('initData')
    result = validate_init_data(init_data)
    return f"<pre>initData: {init_data}\n\nResult: {result}</pre>"
