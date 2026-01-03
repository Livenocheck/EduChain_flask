import os
from flask import Blueprint, request, render_template
from werkzeug.utils import secure_filename
from telegram_tools.telegram_auth import validate_init_data, get_or_create_student
import jwt
from models import db
from models.token_balance import TokenBalance
from models.proof import Proof

bp = Blueprint('upload', __name__, url_prefix='/upload')

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
def upload_page():
    init_data = request.args.get('initData')
    if not init_data:
        return "Unauthorized", 403
    data = validate_init_data(init_data)
    if not data or 'ut' not in data:
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
    
    return render_template('upload.html', student=user, balance=balance_obj.balance, init_data=init_data)

@bp.route('/proof', methods=['POST'])
def upload_proof():
    """Обработка формы с файлом из upload.html"""
    init_data = request.form.get('initData')
    if not init_data:
        return show_alert_page("Ошибка: не авторизован", "", "/tg_app/")
    
    data = validate_init_data(init_data)
    if not data or 'user' not in data:
        return show_alert_page("Ошибка: недействительные данные", init_data)
    
    try:
        user_data = jwt.decode(data['user'], options={"verify_signature": False})
        user = get_or_create_student(user_data['id'], user_data.get('first_name', 'Аноним'))
        
        # Получение данных формы
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        file = request.files.get('file')
        
        if not title:
            return show_alert_page("Ошибка: укажите название достижения", init_data)
        if not file:
            return show_alert_page("Ошибка: выберите файл", init_data)
        
        # Сохранение файла
        filename = secure_filename(file.filename)
        upload_folder = os.path.join('static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        proof = Proof(
            user_id=user.id,
            title=title,
            description=description,
            filename=filename,
            status="pending"
        )
        db.session.add(proof)
        db.session.commit()
        
        return show_alert_page("✅ Достижение отправлено на проверку!", init_data)
        
    except Exception as e:
        # Логировать ошибку в реальном проекте
        return show_alert_page("Ошибка: не удалось обработать файл", init_data)