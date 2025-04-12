from flask import render_template, redirect, url_for, flash, request, jsonify, send_from_directory, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import app, db, mail
from models import User, Event, Photo, PasswordReset
from qr_generator import generate_qr_code
from email_sender import send_qr_code_email, send_password_reset_email
import os
from datetime import datetime, timedelta
import uuid
import base64
from io import BytesIO
from PIL import Image
from flask_mail import Message

# Funções auxiliares
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Contexto global para templates
@app.context_processor
def inject_context():
    return dict(
        wedding_date=app.config['WEDDING_DATE'],
        theme=app.config['THEME'],
        bride_name=app.config['BRIDE_NAME'],
        groom_name=app.config['GROOM_NAME']
    )

# Página inicial
@app.route('/')
def index():
    events = []
    if current_user.is_authenticated:
        # Verificar se o usuário é administrador
        if current_user.is_admin:
            # Administrador vê todos os eventos
            events = Event.query.order_by(Event.created_at.desc()).all()
        else:
            # Usuários normais não vêem eventos, pois apenas admin pode criar
            events = []
    return render_template('index.html', events=events)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            flash('Email ou senha inválidos', 'error')
            return redirect(url_for('login'))
        
        login_user(user)
        next_page = request.args.get('next')
        return redirect(next_page or url_for('index'))
    
    return render_template('login.html')

# Registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Verificar se email já existe
        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Este email já está cadastrado. Você pode recuperar sua senha.', 'info')
            return redirect(url_for('forgot_password', email=email))
        
        # Criar novo usuário
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registro realizado com sucesso!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Esqueci minha senha
@app.route('/esqueci-senha', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    email = request.args.get('email', '')
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Email não encontrado.', 'error')
            return redirect(url_for('forgot_password'))
        
        # Gerar token de reset de senha
        token = PasswordReset.generate_token()
        expires_at = datetime.utcnow() + timedelta(seconds=app.config['PASSWORD_RESET_EXPIRES'])
        
        # Salvar token no banco de dados
        reset = PasswordReset(
            token=token,
            user_id=user.id,
            expires_at=expires_at
        )
        
        db.session.add(reset)
        db.session.commit()
        
        # Enviar email com link para redefinir senha
        reset_url = url_for('reset_password', token=token, _external=True)
        send_password_reset_email(user.email, reset_url)
        
        flash('Um email com instruções para redefinir sua senha foi enviado.', 'success')
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html', email=email)

# Redefinir senha
@app.route('/redefinir-senha/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Buscar token no banco de dados
    reset = PasswordReset.query.filter_by(token=token, used=False).first()
    
    # Verificar se token existe e não expirou
    if not reset or reset.expires_at < datetime.utcnow():
        flash('Link de redefinição de senha inválido ou expirado.', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return redirect(url_for('reset_password', token=token))
        
        # Atualizar senha do usuário
        user = User.query.get(reset.user_id)
        user.password_hash = generate_password_hash(password)
        
        # Marcar token como usado
        reset.used = True
        
        db.session.commit()
        
        flash('Senha redefinida com sucesso!', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)

# Criar evento (apenas para administradores)
@app.route('/criar-evento', methods=['GET', 'POST'])
@login_required
def create_event():
    # Verificar se o usuário é administrador
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
        
        # Criar evento
        new_event = Event(
            name=name,
            description=description,
            date=event_date,
            email=email,
            creator_id=current_user.id
        )
        
        db.session.add(new_event)
        db.session.commit()
        
        # Gerar QR Code
        qr_path = generate_qr_code(
            event_id=new_event.id,
            unique_code=new_event.unique_code,
            base_url=request.host_url
        )
        
        # Atualizar caminho do QR Code no banco de dados
        new_event.qr_code_path = qr_path
        db.session.commit()
        
        # Enviar QR Code por email
        send_qr_code_email(
            to=email,
            event_name=name,
            event_date=event_date,
            qr_path=os.path.join(app.root_path, 'static', qr_path)
        )
        
        flash('Evento criado com sucesso! O QR Code foi enviado para o email informado.', 'success')
        return redirect(url_for('index'))
    
    return render_template('create_event.html')

# Página do evento (acessível via QR Code, sem necessidade de login)
@app.route('/evento/<unique_code>')
def event_page(unique_code):
    event = Event.query.filter_by(unique_code=unique_code).first_or_404()
    return render_template('event.html', event=event)

# Galeria de fotos do evento (acessível via QR Code, sem necessidade de login)
@app.route('/galeria/<unique_code>')
def gallery(unique_code):
    event = Event.query.filter_by(unique_code=unique_code).first_or_404()
    photos = Photo.query.filter_by(event_id=event.id).order_by(Photo.uploaded_at.desc()).all()
    return render_template('gallery.html', event=event, photos=photos)

# Upload de foto diretamente do dispositivo (sem necessidade de login)
@app.route('/upload-foto/<unique_code>', methods=['POST'])
def upload_photo(unique_code):
    event = Event.query.filter_by(unique_code=unique_code).first_or_404()
    
    # Verificar se a foto foi enviada via câmera (base64) ou arquivo
    if 'photo_data' in request.form:
        # Processar imagem Base64 da câmera
        try:
            photo_data = request.form['photo_data']
            if 'data:image/' in photo_data:
                # Remover o prefixo dos dados Base64
                header, encoded = photo_data.split(',', 1)
            else:
                encoded = photo_data
            
            # Decodificar Base64
            decoded_data = base64.b64decode(encoded)
            
            # Gerar nome de arquivo único
            filename = f"{uuid.uuid4()}.jpg"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Salvar imagem no disco
            with open(file_path, 'wb') as f:
                f.write(decoded_data)
            
            # Salvar referência no banco de dados
            user_id = current_user.id if current_user.is_authenticated else None
            
            new_photo = Photo(
                filename=filename,
                event_id=event.id,
                user_id=user_id
            )
            
            db.session.add(new_photo)
            db.session.commit()
            
            return jsonify({'success': True})
        
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    
    elif 'photo_file' in request.files:
        # Processar arquivo da galeria
        file = request.files['photo_file']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado'})
        
        if file and allowed_file(file.filename):
            # Gerar nome de arquivo único
            original_filename = secure_filename(file.filename)
            filename = f"{uuid.uuid4()}_{original_filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Salvar arquivo
            file.save(file_path)
            
            # Salvar referência no banco de dados
            user_id = current_user.id if current_user.is_authenticated else None
            
            new_photo = Photo(
                filename=filename,
                original_filename=original_filename,
                event_id=event.id,
                user_id=user_id
            )
            
            db.session.add(new_photo)
            db.session.commit()
            
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Tipo de arquivo não permitido'})
    
    return jsonify({'success': False, 'message': 'Nenhuma foto enviada'})

# Download de foto (apenas para administradores)
@app.route('/download/<int:photo_id>')
@login_required
def download_photo(photo_id):
    # Verificar se o usuário é administrador
    if not current_user.is_admin:
        flash('Apenas administradores podem baixar fotos', 'error')
        return redirect(url_for('index'))
    
    # Buscar foto pelo ID
    photo = Photo.query.get_or_404(photo_id)
    
    # Enviar arquivo para download
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        photo.filename,
        as_attachment=True,
        download_name=photo.original_filename or photo.filename
    )

# Apagar foto (apenas para administradores)
@app.route('/delete-photo/<int:photo_id>', methods=['POST'])
@login_required
def delete_photo(photo_id):
    # Verificar se o usuário é administrador
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Permissão negada'})
    
    # Buscar foto pelo ID
    photo = Photo.query.get_or_404(photo_id)
    
    try:
        # Apagar arquivo do disco
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Apagar referência no banco de dados
        db.session.delete(photo)
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
