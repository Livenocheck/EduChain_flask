from . import db
from datetime import datetime

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'award', 'purchase', 'transfer'
    amount = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))
    reward_id = db.Column(db.Integer, db.ForeignKey('reward.id'), nullable=True)
    ton_tx_hash = db.Column(db.String(64), nullable=True)  # хеш транзакции в TON
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
