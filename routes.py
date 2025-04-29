from flask import render_template, redirect, url_for, flash, request, jsonify, send_from_directory, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import app, db, mail
from models import User, Event, Photo
from qr_generator import generate_qr_code
from email_sender import send_qr_code_email
import os
from datetime import datetime
import uuid
import base64

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Este email já está cadastrado. Você pode recuperar sua senha.', 'info')
            return redirect(url_for('forgot_password', email=email))
        new_user = User(
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registro realizado com sucesso!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

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
            qr_path=os.path.join(app.root_path, 'static', qr_path)
        )
        flash('Evento criado com sucesso! O QR Code foi enviado para o email informado.', 'success')
        return redirect(url_for('index'))
    return render_template('create_event.html')

@app.route('/evento/<unique_code>')
def event_page(unique_code):
    event = Event.query.filter_by(qr_code=unique_code).first_or_404()
    return render_template('event.html', event=event)

@app.route('/galeria/<unique_code>')
def gallery(unique_code):
    event = Event.query.filter_by(qr_code=unique_code).first_or_404()
    photos = Photo.query.filter_by(event_id=event.id).order_by(Photo.uploaded_at.desc()).all()
    return render_template('gallery.html', event=event, photos=photos)

@app.route('/upload-foto/<unique_code>', methods=['POST'])
def upload_photo(unique_code):
    event = Event.query.filter_by(qr_code=unique_code).first_or_404()
    if 'photo_file' in request.files:
        file = request.files['photo_file']
        if file and allowed_file(file.filename):
            filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            new_photo = Photo(
                filename=filename,
                event_id=event.id
            )
            db.session.add(new_photo)
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Tipo de arquivo não permitido'})
    return jsonify({'success': False, 'message': 'Nenhuma foto enviada'})

@app.route('/download/<int:photo_id>')
@login_required
def download_photo(photo_id):
    if not current_user.is_admin:
        flash('Apenas administradores podem baixar fotos', 'error')
        return redirect(url_for('index'))
    photo = Photo.query.get_or_404(photo_id)
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        photo.filename,
        as_attachment=True
    )

@app.route('/delete-photo/<int:photo_id>', methods=['POST'])
@login_required
def delete_photo(photo_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Permissão negada'})
    photo = Photo.query.get_or_404(photo_id)
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        db.session.delete(photo)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
