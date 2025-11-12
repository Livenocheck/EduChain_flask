from flask import Blueprint, request, render_template
from telegram_tools.telegram_auth import validate_telegram_init_data
import jwt

bp = Blueprint('web', __name__, url_prefix='/admin')

@bp.route('/')
def admin_panel():
    init_data = request.args.get('initData')
    if not init_data:
        return "initData required", 400
    data = validate_telegram_init_data(init_data)
    if not data:
        return "Invalid initData", 403
    user = jwt.decode(data['user'], options={"verify_signature": False})

    return render_template('index.html', 
                         student={'id': user['id'], 'name': user['first_name'], init_data: init_data}) 
