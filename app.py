# app.py corrigido
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configuração segura do DATABASE_URL
db_url = os.getenv('DATABASE_URL')
if not db_url:
    raise RuntimeError("DATABASE_URL não está definida!")
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace('postgres://', 'postgresql://', 1)

app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'dev_key_123'),
    SQLALCHEMY_DATABASE_URI=db_url.replace('postgres://', 'postgresql://', 1),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    UPLOAD_FOLDER=os.path.join(app.static_folder, 'uploads'),
    QRCODE_FOLDER=os.path.join(app.static_folder, 'qrcodes'),
    COVER_FOLDER=os.path.join(app.static_folder, 'covers'),
    MAIL_SERVER=os.getenv('MAIL_SERVER'),
    MAIL_PORT=os.getenv('MAIL_PORT', 587),
    MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', True),
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD')
)

# Garantir criação de pastas
for folder in [app.config['UPLOAD_FOLDER'], 
               app.config['QRCODE_FOLDER'], 
               app.config['COVER_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
mail = Mail(app)
migrate = Migrate(app, db)

from models import User, Event, Photo

@app.before_first_request
def create_admin():
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@eventos.com')
    if not User.query.filter_by(email=admin_email).first():
        from werkzeug.security import generate_password_hash
        admin = User(
            email=admin_email,
            password=generate_password_hash(os.getenv('ADMIN_PASSWORD', 'admin123')),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

from routes import *

if __name__ == '__main__':
    app.run()
