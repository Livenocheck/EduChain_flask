from . import db
from datetime import datetime

class Transaction(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'award', 'purchase'
    amount = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))
    reward_id = db.Column(db.Integer, db.ForeignKey('reward.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
