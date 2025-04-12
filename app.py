# app.py atualizado e corrigido
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_mail import Mail
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv
from datetime import datetime

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar extensões
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Configurações do app
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev_key_123'),
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL').replace('postgres://', 'postgresql://', 1),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(app.static_folder, 'uploads'),
        QRCODE_FOLDER=os.path.join(app.static_folder, 'qrcodes'),
        COVER_FOLDER=os.path.join(app.static_folder, 'covers'),
        MAIL_SERVER=os.getenv('MAIL_SERVER'),
        MAIL_PORT=int(os.getenv('MAIL_PORT', 587)),
        MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', 'True').lower() in ('true', '1'),
        MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
        MAIL_PASSWORD=os.getenv('MAIL_PASSWORD')
    )

    # Criar pastas necessárias
    for folder in [app.config['UPLOAD_FOLDER'], 
                   app.config['QRCODE_FOLDER'], 
                   app.config['COVER_FOLDER']]:
        os.makedirs(folder, exist_ok=True)

    # Inicializar extensões com o app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # Configurar modelos
    class User(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(100), unique=True, nullable=False)
        password = db.Column(db.String(200), nullable=False)
        is_admin = db.Column(db.Boolean, default=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

    class Event(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(200), nullable=False)
        description = db.Column(db.Text)
        date = db.Column(db.DateTime, nullable=False)
        cover_image = db.Column(db.String(200))
        qr_code = db.Column(db.String(200))
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

    class Photo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        filename = db.Column(db.String(200), nullable=False)
        event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
        uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Criar admin no contexto da aplicação
    with app.app_context():
        db.create_all()
        
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@eventos.com')
        admin_password = os.getenv('ADMIN_PASSWORD')
        
        if not User.query.filter_by(email=admin_email).first():
            admin = User(
                email=admin_email,
                password=generate_password_hash(admin_password),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Administrador criado com sucesso")

    # Configurar rotas
    @app.route('/')
    def index():
        return "Página inicial - Implementar template"

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        return "Página de login - Implementar template"

    @app.route('/criar-evento', methods=['GET', 'POST'])
    def create_event():
        return "Criação de evento - Implementar template"

    # ... (adicionar outras rotas necessárias)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

