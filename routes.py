from flask import render_template, redirect, url_for, flash, request, jsonify, send_from_directory, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from extensions import db
from models import User, Event, Photo
from qr_generator import generate_qr_code
from email_sender import send_qr_code_email
import os
from datetime import datetime
import uuid

def register_routes(app):
    @app.route('/')
    def index():
        events = []
        if current_user.is_authenticated and current_user.is_admin:
            events = Event.query.order_by(Event.created_at.desc()).all()
        return render_template('index.html', events=events)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            user = User.query.filter_by(email=email).first()
            if not user or not check_password_hash(user.password, password):
                flash('Email ou senha inválidos', 'error')
                return redirect(url_for('login'))
            login_user(user)
            return redirect(url_for('index'))
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/criar-evento', methods=['GET', 'POST'])
    @login_required
    def create_event():
        if not current_user.is_admin:
            flash('Apenas administradores podem criar eventos.', 'error')
            return redirect(url_for('index'))
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            date_str = request.form.get('date')
            email = request.form.get('email')
            if not all([name, date_str, email]):
                flash('Por favor, preencha todos os campos obrigatórios', 'error')
                return redirect(url_for('create_event'))
            try:
                event_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Formato de data inválido', 'error')
                return redirect(url_for('create_event'))
            new_event = Event(
                name=name,
                description=description,
                date=event_date,
            )
            db.session.add(new_event)
            db.session.commit()
            qr_path = generate_qr_code(
                event_id=new_event.id,
                unique_code=str(uuid.uuid4()),
                base_url=request.host_url
            )
            new_event.qr_code = qr_path
            db.session.commit()
            send_qr_code_email(
                to=email,
                event_name=name,
                event_date=event_date,
                qr_path=os.path.join(app.static_folder, qr_path)
            )
            flash('Evento criado com sucesso! O QR Code foi enviado para o email informado.', 'success')
            return redirect(url_for('index'))
        return render_template('create_event.html')

    # ... (adiciona aqui outras rotas conforme necessário)
