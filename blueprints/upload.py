import os
from flask import Blueprint, request, render_template
from werkzeug.utils import secure_filename
from telegram_tools.telegram_auth import validate_init_data, get_or_create_student
import jwt
from models import db
from models.token_balance import TokenBalance

bp = Blueprint('upload', __name__, url_prefix='/upload')

@bp.route('/')
def upload_page():
    return render_template('upload.html')

@bp.route('/proof', methods=['POST'])
def upload_proof():
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
    
    try:
        user_data = jwt.decode(data['user'], options={"verify_signature": False})
        user = get_or_create_student(user_data['id'], user_data.get('first_name', 'Аноним'))
        
        title = request.form.get('title', '').strip()
        if not title:
            return '''
            <!DOCTYPE html><html><body>
                <script src="https://telegram.org/js/telegram-web-app.js"></script>
                <script>Telegram.WebApp.showAlert("Ошибка: укажите название"); setTimeout(() => history.back(), 1500);</script>
            </body></html>
            '''
        
        file = request.files.get('file')
        if file and file.filename:
            filename = secure_filename(file.filename)
            upload_folder = os.path.join('static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file.save(os.path.join(upload_folder, filename))
        
        # TODO: Сохранить в БД Proof (если нужно)
        
        return '''
        <!DOCTYPE html><html><body>
            <script src="https://telegram.org/js/telegram-web-app.js"></script>
            <script>Telegram.WebApp.showAlert("✅ Достижение отправлено на проверку!"); setTimeout(() => window.location.href="/tg_app/", 1500);</script>
        </body></html>
        '''
    except Exception as e:
        return '''
        <!DOCTYPE html><html><body>
            <script src="https://telegram.org/js/telegram-web-app.js"></script>
            <script>Telegram.WebApp.showAlert("Ошибка обработки файла"); setTimeout(() => history.back(), 1500);</script>
        </body></html>
        '''