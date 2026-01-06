import os
from flask import Blueprint, request, render_template, flash, redirect, session, url_for
from functools import wraps
from werkzeug.utils import secure_filename
from models import db
from models.user import User
from models.proof import Proof

bp = Blueprint('upload', __name__, url_prefix='/upload')

# Повторяем декоратор здесь, чтобы избежать импорта из main_bp (пока)
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
def upload_page():
    user = User.query.get(session['user_id'])
    return render_template('upload.html', show_form=True)

@bp.route('/proof', methods=['POST'])
@student_required
def upload_proof():
    user = User.query.get(session['user_id'])
    
    title = request.form.get('title', '').strip()
    if not title:
        flash("❌ Укажите название", "error")
        return render_template('upload.html', show_form=True)
    
    file = request.files.get('file')
    if file and file.filename:
        filename = secure_filename(file.filename)
        upload_folder = os.path.join('static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, filename))
    else:
        flash("❌ Выберите файл", "error")
        return render_template('upload.html', show_form=True)
    
    proof = Proof(
        user_id=user.id,
        title=title,
        filename=f"/static/uploads/{filename}",
        status="pending"
    )

    db.session.add(proof)
    db.session.commit()
    
    flash("✅ Достижение отправлено на проверку!", "success")
    return render_template('upload.html', show_form=False)
