from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .school import School
from .student import Student
from .token import Reward, TokenBalance
from .transaction import Transaction
