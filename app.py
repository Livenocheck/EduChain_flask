from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from models import db
# from config import Config
# from dotenv import load_dotenv
# from os import getenv #, path


# load_dotenv() # загрузка переменных окружения из .env файла (если потребуется)

app = Flask(__name__)
# app.config.from_object(Config)  # загрузка всех настроек
# db.init_app(app) # инициализация базы данных с приложением Flask

@app.route('/')
def hello_world():
  return 'Hello, World!'

if __name__ == '__main__':
  app.run(debug=True)
