from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_mailman import Mail
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin import Admin


class Base(DeclarativeBase):
    pass


# Inicialização dos objetos globais
db = SQLAlchemy(metadata=Base.metadata)
ma = Marshmallow()
migrate = Migrate()
mail = Mail()
jwt = JWTManager()
login_manager = LoginManager()
admin = Admin(name='SGCD - Painel Administrativo',
              template_mode='bootstrap4')
