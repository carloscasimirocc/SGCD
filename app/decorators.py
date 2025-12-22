from functools import wraps
from flask import abort
from flask_login import current_user


def roles_required(*roles):
    '''Permite acesso apenas a utilizadores com um dos perfis informados.'''
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            if current_user.perfil.value not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
