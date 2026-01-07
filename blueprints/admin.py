import os
from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from models import db
from models.user import User
from models.token_balance import TokenBalance
from models.reward import Reward
from models.transaction import Transaction
from models.school import School
from models.proof import Proof
from werkzeug.utils import secure_filename
from functools import wraps

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
def index():
    # /admin → проверка сессии
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.panel'))
    return redirect(url_for('admin.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Форма входа
    if request.method == 'POST':
        if request.form['password'] == os.getenv('ADMIN_PASSWORD'):
            session['admin_logged_in'] = True
            return redirect(url_for('admin.panel'))
        return render_template('admin_login.html', error="Неверный пароль")
    return render_template('admin_login.html')


@bp.route('/panel')
@admin_required
def panel():
    school = School.query.first()
    if not school:
        school = School(name="EduChain School")
        db.session.add(school)
        db.session.commit()
    students = User.query.filter_by(school_id=school.id).all()
    rewards = Reward.query.filter_by(school_id=school.id).all()
    return render_template('admin.html', students=students, rewards=rewards)

@bp.route('/award', methods=['POST'])
@admin_required
def award():
    user_id = int(request.form['user_id'])
    amount = int(request.form['amount'])
    
    balance = TokenBalance.query.filter_by(user_id=user_id).first()
    if not balance:
        balance = TokenBalance(user_id=user_id, balance=0)
        db.session.add(balance)
    
    balance.balance += amount
    tx = Transaction(user_id=user_id, type='award', amount=amount, description="Начислено админом")
    db.session.add(tx)
    db.session.commit()
    return redirect(url_for('admin.panel'))

@bp.route('/add_reward', methods=['POST'])
@admin_required
def add_reward():
    file = request.files.get('image')
    filename = None
    if file and file.filename:
        filename = secure_filename(file.filename)
        file.save(os.path.join('static', 'uploads', filename))
    
    school = School.query.first()
    if not school:
        school = School(name="EduChain School")
        db.session.add(school)
        db.session.commit()
    
    reward = Reward(
        name=request.form['name'],
        cost=int(request.form['cost']),
        description=request.form.get('description', ''),
        image_filename=f"static/uploads/{filename}",
        quantity=int(request.form['quantity']) if request.form.get('quantity') else None,
        school_id=school.id
    )
    db.session.add(reward)
    db.session.commit()
    return redirect(url_for('admin.panel'))

@bp.route('/delete_reward/<int:reward_id>', methods=['POST'])
@admin_required
def delete_reward(reward_id):
    reward = Reward.query.get_or_404(reward_id)
    db.session.delete(reward)
    db.session.commit()
    return redirect(url_for('admin.panel'))

@bp.route('/proofs')
@admin_required
def view_proofs():
    pending_proofs = Proof.query.filter_by(status="pending").all()
    return render_template('admin_proofs.html', proofs=pending_proofs)

@bp.route('/proof/<int:proof_id>/approve', methods=['POST'])
@admin_required
def approve_proof(proof_id):
    proof = Proof.query.get(proof_id)
    if proof:
        tokens = int(request.form.get('tokens', 0))
        proof.status = "approved"
        proof.tokens_awarded = tokens
        
        # Начисляем токены ученику
        balance = TokenBalance.query.filter_by(user_id=proof.user_id).first()
        if balance:
            balance.balance += tokens
        else:
            db.session.add(TokenBalance(user_id=proof.user_id, balance=tokens))
        
        db.session.commit()
        flash(f"✅ Достижение одобрено! Начислено {tokens} токенов", "success")
    return redirect('/admin/proofs')

@bp.route('/proof/<int:proof_id>/reject', methods=['POST'])
@admin_required
def reject_proof(proof_id):
    proof = Proof.query.get(proof_id)
    if proof:
        proof.status = "rejected"
        db.session.commit()
        flash("❌ Достижение отклонено", "error")
    return redirect('/admin/proofs')

@bp.route('/verification')
@admin_required
def verification():
    users = User.query.filter_by(
        verification_requested=True,
        verified=False
    ).all()
    return render_template('admin_verification.html', users=users)

@bp.route('/verify/<int:user_id>', methods=['POST'])
@admin_required
def verify_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.verified = True
        db.session.commit()
        flash("✅ Ученик верифицирован!", "success")
    return redirect('/admin/verification')

@bp.route('/reject_verification/<int:user_id>', methods=['POST'])
@admin_required
def reject_verification(user_id):
    user = User.query.get(user_id)
    if user:
        user.verification_rejected = True
        user.verification_requested = False  # Сбросить запрос
        reason = request.form.get('reason', '').strip()
        if reason:
            user.rejection_reason = reason
        db.session.commit()
        flash("❌ Верификация отклонена", "error")
    return redirect('/admin/verification')

@bp.route('/logout')
@admin_required
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))
