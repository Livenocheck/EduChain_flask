from . import db

class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    public_token_symbol = db.Column(db.String(10), default="SCH")
    ton_wallet_address = db.Column(db.String(64), nullable=True)  # адрес школьного токена
