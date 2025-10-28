import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'educhain-dev-secret')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///educhain.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    TON_MNEMONIC = os.getenv('TON_MNEMONIC')  # для кошелька школы
    TON_NETWORK = os.getenv('TON_NETWORK', 'testnet')  # или 'mainnet'
