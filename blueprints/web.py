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
            user_data = jwt.decode(data['user'], options={"verify_signature": False})
            user = get_or_create_student(user_data['id'], user_data.get('first_name', 'Аноним'))
            return redirect(f"/tg_app?initData={init_data}")
    return render_template('index.html')
