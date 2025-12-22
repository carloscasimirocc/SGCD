from app.utilizadores.models import Utilizador, db
from flask import redirect, url_for, flash
from flask_login import current_user
from functools import wraps


class AdminUserService:

    @staticmethod
    def listar_utilizadores():
        # Retorna todos os utilizadores
        return db.session.query(Utilizador).all()

    @staticmethod
    def buscar_utilizador_por_id(user_id):
        return db.session.get(Utilizador, user_id)

    @staticmethod
    def remover_utilizador(user_id):
        user = db.session.get(Utilizador, user_id)
        if not user:
            return False

        db.session.delete(user)
        db.session.commit()
        return True

    @staticmethod
    def actualizar_utilizador(user_id, **data):
        user = db.session.get(Utilizador, user_id)
        if user:
            db.sessionx.update(**data)
            db.session.commit()
            return True
        return False


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acesso restrito a administradores.', 'danger')
            return redirect(url_for('autenticacao.login'))
        return f(*args, **kwargs)

    return decorated_function
