from . import db

class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    public_token_ticker = db.Column(db.String(10), unique=True, default="SCH") # Тикер публичного токена школы (как "USDT")
    public_jetton_master_address = db.Column(db.String(64), unique=True, nullable=True)
    '''public_jetton_master_address - уникальный идентификатор ПУБЛИЧНОГО школьного токена в TON. 
    По этому адресу можно:
 - Посмотреть токен на tonviewer.com
 - Добавить его в кошелёк (Telegram Wallet, Tonkeeper)
 - Торговать на биржах (STON.fi, DeDust)
    '''
    admin_code_hash = db.Column(db.String(128), nullable=False)  # хеш кода для админа школы
