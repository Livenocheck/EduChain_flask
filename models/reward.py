from . import db

class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))
    image_filename = db.Column(db.String(100))
    quantity = db.Column(db.Integer, nullable=True)  # None = unlimited
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
