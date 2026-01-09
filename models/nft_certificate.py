from . import db
from datetime import datetime

class NFTCertificate(db.Model):
    __tablename__ = 'nft_certificate'
    
    id = db.Column(db.Integer, primary_key=True)
    owner_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(200))
    description = db.Column(db.Text)
    transaction_hash = db.Column(db.String(64))
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    minted_at = db.Column(db.DateTime)