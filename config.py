from os import getenv #, path

class Config:
    SECRET_DEV_KEY = getenv('SECRET_DEV_KEY')
    DATABASE_URI = getenv('DATABASE_URI', 'sqlite:///educhain.db') # value, default
    SQLALCHEMY_TRACK_MODIFICATIONS = getenv('SQLALCHEMY_TRACK_MODIFICATIONS', False) # False (по умолчанию) отключает отслеживание изменений объектов, повышает производительность
    TG_BOT_TOKEN = getenv('TG_BOT_TOKEN')

    # VK_API_TOKEN = getenv('VK_API_TOKEN')

    # upload_folder = path.join(path.dirname(path.abspath(__file__)), 'static', 'uploads')
    # ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
    # MAX_CONTENT_LENGTH = 5 * 1024 * 1024 # 5 MB limit for uploaded files
