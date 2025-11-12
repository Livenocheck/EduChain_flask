from os import getenv
import hmac
import hashlib
from urllib.parse import unquote

def validate_telegram_init_data(init_data) -> dict:
    bot_token = getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        return None
    try:
        pairs = [pair.split('=', 1) for pair in init_data.split('&')]
        data = {key: unquote(value) for key, value in pairs}
        
        # Извлекаем хеш
        received_hash = data.pop('hash', None)
        if not received_hash:
            return None
        
        # Строим строку для проверки
        data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(data.items()))
        
        # Генерируем секретный ключ
        secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        
        # Считаем хеш
        computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        # Проверяем хеш и срок действия
        if computed_hash != received_hash:
            return None
        
        if 'auth_date' in data:
            import time
            if time.time() - int(data['auth_date']) > 86400:  # 24 часа
                return None
        
        return data
    except Exception:
        return None
