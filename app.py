import os
from flask import Flask
from models import db
from blueprints.web import bp as web_bp
from blueprints.admin import bp as admin_bp
from blueprints.main_bp import bp as main_bp
from blueprints.marketplace import bp as marketplace_bp
from blueprints.upload import bp as upload_bp
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Создаём папку для загрузок
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Инициализируем БД
    db.init_app(app)
    
    # Инициализируем миграции
    migrate = Migrate(app, db)
    
    # Регистрируем blueprints
    blueprints = (web_bp, admin_bp, main_bp, marketplace_bp, upload_bp)

    for blueprint in blueprints:
        app.register_blueprint(blueprint)
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)