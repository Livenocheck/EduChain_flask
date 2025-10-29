from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    public_token_ticker = db.Column(db.String(10), default="SCH") # Тикер публичного токена школы (как "USDT")
    public_jetton_master_address = db.Column(db.String(64), nullable=True)
    '''public_jetton_master_address - уникальный идентификатор ПУБЛИЧНОГО школьного токена в TON. 
    По этому адресу можно:
 - Посмотреть токен на tonviewer.com
 - Добавить его в кошелёк (Telegram Wallet, Tonkeeper)
 - Торговать на биржах (STON.fi, DeDust)
    '''

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary_key=True указывает на то что id - первичный ключ таблицы в БД
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False)
    # vk_id = db.column(db.BigInteger, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)

class TokenBalance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    balance = db.Column(db.Integer, default=0)

class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))
    image_filename = db.Column(db.String(100))
    quantity = db.Column(db.Integer, nullable=True)  # None = unlimited
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)

class Transaction(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'award', 'purchase'
    amount = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
