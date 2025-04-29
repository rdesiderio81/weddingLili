from flask import Flask
from extensions import db, login_manager, mail, migrate
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from routes import register_routes
        register_routes(app)
        db.create_all()
        from models import User
        from werkzeug.security import generate_password_hash
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@eventos.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        if not User.query.filter_by(email=admin_email).first():
            admin = User(
                email=admin_email,
                password=generate_password_hash(admin_password),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Administrador criado com sucesso")
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
