# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY'),
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL').replace('postgres://', 'postgresql://'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    UPLOAD_FOLDER=os.path.join(app.static_folder, 'uploads'),
    QRCODE_FOLDER=os.path.join(app.static_folder, 'qrcodes'),
    COVER_FOLDER=os.path.join(app.static_folder, 'covers'),
    MAIL_SERVER=os.getenv('MAIL_SERVER'),
    MAIL_PORT=os.getenv('MAIL_PORT'),
    MAIL_USE_TLS=os.getenv('MAIL_USE_TLS'),
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD')
)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
mail = Mail(app)
migrate = Migrate(app, db)

# Importar após inicialização para evitar circular imports
from models import User
from routes import *

# Criar admin padrão se não existir
@app.before_first_request
def create_admin():
    admin_email = os.getenv('ADMIN_EMAIL')
    if not User.query.filter_by(email=admin_email).first():
        from werkzeug.security import generate_password_hash
        admin = User(
            email=admin_email,
            password=generate_password_hash(os.getenv('ADMIN_PASSWORD')),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run()
