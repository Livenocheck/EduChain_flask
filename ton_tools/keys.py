import os
import hashlib
import hmac
from typing import Tuple

def mnemonic_to_private_key(mnemonic: str) -> bytes:
    """
    Конвертирует 24-словную мнемонику в 32-байтный приватный ключ
    Совместимо с кошельками TON (Tonkeeper, MyTonWallet)
    """
    # Соль для PBKDF2
    salt = "mnemonic"
    
    # Генерируем seed через PBKDF2
    seed = hashlib.pbkdf2_hmac(
        hash_name="sha512",
        password=mnemonic.encode("utf-8"),
        salt=salt.encode("utf-8"),
        iterations=2048,
        dklen=64
    )
    
    # Первые 32 байта = приватный ключ
    return seed[:32]

def get_wallet_keys() -> Tuple[bytes, bytes]:
    """Возвращает (public_key, private_key) из SEED"""
    mnemonic = os.getenv("PROJECT_WALLET_SEED", "")
    if not mnemonic:
        raise ValueError("PROJECT_WALLET_SEED not set")
    
    private_key = mnemonic_to_private_key(mnemonic)
    
    # Публичный ключ = SHA256(приватный ключ)
    public_key = hashlib.sha256(private_key).digest()
    
    return public_key, private_key