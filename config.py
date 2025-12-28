import os
from pathlib import Path

from dotenv import load_dotenv

# Carrega variáveis do arquivo instance/.env
base_dir = Path(__file__).parent

dotenv_path = base_dir/'instance'/'.env'

load_dotenv(dotenv_path=dotenv_path)
print(dotenv_path)


class Config:
    '''Configurações do e-mail.'''

    # Chave secreta e token JWT
    SECRET_KEY = os.getenv('SECRET_KEY', 'hard-to-guess-string')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'chave_jwt_padrao')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1h em segundos

    # Configurar e-mail flask-mailman
    # MAIL_SERVER = os.getenv('MAIL_SERVER')
    # MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    # MAIL_PORT = os.getenv('MAIL_PORT', '787')
    # MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    # MAIL_API_KEY = os.getenv('MAIL_API_KEY')
    # MAIL_FROM = os.getenv('MAIL_FROM')

    # Configuração do Flask-Mailman para MailerSend SMTP
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.mailersend.net')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in [
        'true', 't', '1']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_FROM', 'no-reply@decifer.site')
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL = False')

    # Configurar o flask-admin
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    FLASK_ADMIN_SWATCH = 'cerulean'

    # Configurar o banco de dados
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEV_DATABASE_URI = os.getenv('DEV_DATABASE_URI')

    # Configurar ambiente
    DEBUG = True


class DevelopmentConfig(Config):
    '''Configurações para ambiente de desenvolvimento.'''
    DEBUG = True
    DEV_DATABASE_URI = os.getenv('DEV_DATABASE_URI')


class ProductionConfig(Config):
    '''Configurações para ambiente de produção.'''
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError ('SECRET_KEY não definida no ambiente')
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('PROD_DATABASE_URI')


class TestingConfig(Config):
    '''Configurações para testes.'''
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URI')


config = {
    'desenvolvimento': DevelopmentConfig,
    'teste': TestingConfig,
    'producao': ProductionConfig,
    'default': DevelopmentConfig,
}
