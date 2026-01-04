import os
import hmac
import hashlib
from urllib.parse import unquote
import jwt
from models import db
from models.user import User
from models.school import School
from models.token_balance import TokenBalance

# telegram_tools/telegram_auth.py
import os
import hmac
import hashlib
from urllib.parse import unquote

def validate_init_data(init_data):
    bot_token = os.getenv('BOT_TOKEN')
    print(f"DEBUG: BOT_TOKEN = {bot_token[:10] if bot_token else 'None'}")
    print(f"DEBUG: init_data length = {len(init_data) if init_data else 0}")
    
    if not bot_token or not init_data:
        print("DEBUG: Missing bot_token or init_data")
        return None
    
    try:
        pairs = [pair.split('=', 1) for pair in init_data.split('&')]
        data = {key: unquote(value) for key, value in pairs}
        received_hash = data.pop('hash', None)
        print(f"DEBUG: Received hash = {received_hash}")
        
        if not received_hash:
            print("DEBUG: No hash in initData")
            return None
        
        data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(data.items()))
        secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        print(f"DEBUG: Computed hash = {computed_hash}")
        print(f"DEBUG: Hashes match = {computed_hash == received_hash}")
        
        if computed_hash != received_hash:
            return None
        return data
    except Exception as e:
        print(f"DEBUG: Exception in validate_init_data: {e}")
        return None

def get_or_create_student(telegram_id, name):
    user = User.query.filter_by(telegram_id=telegram_id).first()
    if user:
        return user
    
    school = School.query.first()
    if not school:
        school = School()
        db.session.add(school)
        db.session.commit()
    
    user = User(telegram_id=telegram_id, name=name, school_id=school.id, role="student")
    db.session.add(user)
    db.session.commit()
    
    balance = TokenBalance(user_id=user.id, balance=0)
    db.session.add(balance)
    db.session.commit()
    
    return user
    