from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .school import School
from .user import User
from .token_balance import TokenBalance
from .reward import Reward
from .transaction import Transaction
from .proof import Proof
