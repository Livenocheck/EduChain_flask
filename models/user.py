from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary_key=True указывает на то что id - первичный ключ таблицы в БД
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False)
    # vk_id = db.column(db.BigInteger, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    role = db.Column(db.String(20), default="student")  # "student", "admin"
    # ton_wallet = db.Column(db.String(100), nullable=True)