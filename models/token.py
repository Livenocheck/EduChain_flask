from . import db

class TokenBalance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    balance = db.Column(db.Integer, default=0)

class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=True)  # None = unlimited
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
