from flask import Flask
from config import config
from app.extensions import db, ma, migrate, jwt,  login_manager, admin, mail
from app.autenticacao.routes import autenticacao_bp
from app.publico.routes import publico_bp
from app.relatorios.routes import relatorio_bp

from app.cli import criar_admin  # importa o comando
from datetime import datetime


# Criação da aplicação Flask


def create_app(config_name='desenvolvimento'):
    'Criar a aplicação Flask no modo desenvolvimento'

    # instancia do Flask
    app = Flask(__name__)

    # carregar configuração base
    app.config.from_object(config[config_name])

    # Inicializar as extensões
    db.init_app(app)

    ma.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    login_manager.init_app(app)
    admin.init_app(app)
    app.cli.add_command(criar_admin)
    mail.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # import local para evitar import circular
        from app.utilizadores.models import Utilizador
        try:
            return db.session.get(Utilizador, int(user_id))
        except Exception:
            return None

    from app.utilizadores.models import Anonymous
    # regista a classe anónima para que current_user.perfil exista mesmo sem login
    login_manager.anonymous_user = Anonymous

    # Adiciona os modelos ao painel admin
    # garantir que os modelos do historico estão carregados (registam os mappers)
    # isto evita que o mapper de Utilizador seja inicializado antes do
    # HistoricoAlteracaoPerfil, o que causa InvalidRequestError
    from app.historico.models import HistoricoAlteracaoPerfil

    from app.utilizadores.models import DadosAdministrador, Utilizador, DadosProfessor, DadosAluno, ApenasAdminView
    admin.add_view(ApenasAdminView(DadosAdministrador, db.session))
    admin.add_view(ApenasAdminView(Utilizador, db.session))
    admin.add_view(ApenasAdminView(DadosProfessor, db.session))
    admin.add_view(ApenasAdminView(DadosAluno, db.session))

    # Registar blueprints da home
    app.register_blueprint(publico_bp, url_prefix='/')

    # Registar os blueprints das outras rotas
    app.register_blueprint(autenticacao_bp, url_prefix='/auth')

    # Registar os blueprints das outras rotas
    app.register_blueprint(relatorio_bp, url_prefix='/perfil')

    from datetime import datetime, timezone

    @app.context_processor
    def inject_current_year():
        return {'current_year': datetime.now(timezone.utc).year}

    return app
