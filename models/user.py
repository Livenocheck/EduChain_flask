from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False)
    # vk_id = db.column(db.BigInteger, unique=True, nullable=False)
    first_name = db.Column(db.String(50))      # Имя (реальное)
    last_name = db.Column(db.String(50))       # Фамилия
    # patronymic = db.Column(db.String(50))    # Отчество (опционально)
    verified = db.Column(db.Boolean, default=False)  # False = ожидает проверки
    verification_requested = db.Column(db.Boolean, default=False)
    verification_rejected = db.Column(db.Boolean, default=False)
    grade = db.Column(db.String(10))
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    role = db.Column(db.String(20), default="student")  # "student", "admin"
    #ton_wallet = db.Column(db.String(100))
    eth_wallet = db.Column(db.String(100))