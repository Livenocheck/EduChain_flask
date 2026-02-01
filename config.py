from os import getenv, path, makedirs

class Config:
    if getenv('RENDER'):
        DB_PATH = '/opt/render/project/src/instance/educhain.db'
        makedirs(path.dirname(DB_PATH), exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/educhain.db'
    
    SECRET_KEY = getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = getenv('DATABASE_URI', 'sqlite:///educhain.db') # value, default
    SQLALCHEMY_TRACK_MODIFICATIONS = getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False').lower() == 'true' 
    # /\ False (по умолчанию) отключает отслеживание изменений объектов, повышает производительность
    
    BOT_TOKEN = getenv('TG_BOT_TOKEN')

    # VK_API_TOKEN = getenv('VK_API_TOKEN')
    SUBFOLDERS = ['uploads', 'rewards_md', 'nft_uploads', 'nft_metadata']
    UPLOAD_FOLDER = path.join(path.dirname(path.abspath(__file__)), 'static')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 
