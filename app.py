from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os
from datetime import datetime, timedelta
import secrets

# Inicializar aplicação Flask
app = Flask(__name__)
app.config.from_pyfile('config.py')

# Garantir que as pastas de upload existam
os.makedirs(os.path.join(app.static_folder, 'uploads'), exist_ok=True)
os.makedirs(os.path.join(app.static_folder, 'qrcodes'), exist_ok=True)
os.makedirs(os.path.join(app.static_folder, 'img'), exist_ok=True)

# Inicializar extensões
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)

# Importar para evitar importações circulares
from models import User, Event, Photo, PasswordReset

# Inicializar o banco de dados dentro do contexto da aplicação
with app.app_context():
    db.create_all()
    
    # Criar usuário administrador se não existir
    from werkzeug.security import generate_password_hash
    admin = User.query.filter_by(email='admin@eventos.com').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@eventos.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Usuário administrador criado!")

# Importar rotas após configuração inicial
import routes

if __name__ == '__main__':
    app.run(debug=True)
