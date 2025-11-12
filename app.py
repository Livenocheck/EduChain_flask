from flask import Flask #, request, render_template, jsonify
from blueprints.web import bp as web_bp
# from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db
from config import Config
#from telegram_tools import validate_telegram_init_data
# from dotenv import load_dotenv # загрузка переменных окружения (если потребуется)
from os import getenv #, path
# import jwt


# load_dotenv() # загрузка переменных окружения из .env файла (если потребуется)

def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)  # загрузка всех настроек
    db.init_app(app) # инициализация базы данных с приложением Flask

    app.register_blueprint(web_bp) # регистрация блюпринта (маршруты веб-приложения)

    return app


if __name__ == '__main__':
    app = create_app()
    migrate = Migrate(app, db)  # инициализация миграций
    app.run(debug=True)
