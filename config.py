import os
from datetime import datetime

# Configurações básicas
SECRET_KEY = 'evento_ligia_paulo_2025'
BASEDIR = os.path.abspath(os.path.dirname(__file__))

# Configurações do banco de dados
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'eventos.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Configurações de upload
UPLOAD_FOLDER = os.path.join(BASEDIR, 'static', 'uploads')
QRCODE_FOLDER = os.path.join(BASEDIR, 'static', 'qrcodes')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB limite máximo

# Configuração de email
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'casamentoligiaepaulo@gmail.com'
MAIL_PASSWORD = 'gpbihptextqwsfgp'  # Substitua pela senha de aplicativo gerada do Gmail
MAIL_DEFAULT_SENDER = 'casamentoligiaepaulo@gmail.com'

# Link de reset de senha válido por 24 horas
PASSWORD_RESET_EXPIRES = 86400  # segundos (24 horas)

# Data do casamento
WEDDING_DATE = datetime(2025, 5, 17)

# Tema e cores
THEME = {
    'primary_color': '#E6E6FA',  # Lilás claro
    'secondary_color': '#F5F5DC',  # Bege
    'font_primary': 'Playfair Display, serif',
    'font_secondary': 'Montserrat, sans-serif'
}

# Nome dos noivos
BRIDE_NAME = 'Lígia'
GROOM_NAME = 'Paulo'
