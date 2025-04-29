import os
from datetime import datetime

SECRET_KEY = os.getenv('SECRET_KEY', 'evento_ligia_paulo_2025')
BASEDIR = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(BASEDIR, 'eventos.db')).replace('postgres://', 'postgresql://', 1)
SQLALCHEMY_TRACK_MODIFICATIONS = False

UPLOAD_FOLDER = os.path.join(BASEDIR, 'static', 'uploads')
QRCODE_FOLDER = os.path.join(BASEDIR, 'static', 'qrcodes')
COVER_FOLDER = os.path.join(BASEDIR, 'static', 'covers')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ('true', '1')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')

PASSWORD_RESET_EXPIRES = 86400
WEDDING_DATE = datetime(2025, 5, 17)
THEME = {
    'primary_color': '#E6E6FA',
    'secondary_color': '#F5F5DC',
    'font_primary': 'Playfair Display, serif',
    'font_secondary': 'Montserrat, sans-serif'
}
BRIDE_NAME = 'Lígia'
GROOM_NAME = 'Paulo'
