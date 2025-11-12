from . import db
from datetime import datetime

class AchievementProof(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_name = db.Column(db.String(100), nullable=False)
    file_data = db.Column(db.LargeBinary, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
