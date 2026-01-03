from flask import Blueprint, request, render_template, redirect
from telegram_tools.telegram_auth import validate_init_data, get_or_create_student
import jwt

bp = Blueprint('web', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

