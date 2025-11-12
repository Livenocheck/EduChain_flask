from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .school import School
from .user import User
from .token_balance import TokenBalance
from .reward import Reward
from .transaction import Transaction
from .bug_report import BugReport
from .feedback import Feedback
from .achievement_proof import AchievementProof
