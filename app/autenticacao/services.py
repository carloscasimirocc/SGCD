from typing import Dict, Any, cast

from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from flask_login import login_user

from app.autenticacao.schemas import CadastrarSchema
from app.utilizadores.models import Utilizador, DadosCliente
from app.extensions import db
import logging
import traceback
from flask import current_app

logger = logging.getLogger(__name__)


class CadastrarService:
    @staticmethod
    def cadastrar(dados_brutos: Dict[str, Any]) -> Dict[str, Any]:

        # validar os dados com schema
        cadastrar = CadastrarSchema()
        try:
            # validação dos dados por parte do schema
            logger.debug('CadastrarService: dados_brutos=%s', dados_brutos)
            dados_validos_raw = cadastrar.load(dados_brutos)

            # Afirmação de tipo explícita para o Pylance
            dados_validos: Dict[str, Any] = cast(
                Dict[str, Any], dados_validos_raw)

            # tratamento da senha
            senha_pura = dados_validos.pop('senha')

            # instanciar a classe Cliente com dados limpos
            novo_cliente = Utilizador(**dados_validos)
            novo_cliente.dados_cliente = DadosCliente()

            # gerar hash da senha
            novo_cliente.definir_senha(senha_pura)

            db.session.add(novo_cliente)
            db.session.commit()

            login_user(novo_cliente)

            return {'success': True, 'msg': 'Utilizador criado com sucesso'}

        except ValidationError as err:
            # erros de validação no marshmallow (schema)
            logger.debug('CadastrarService: ValidationError %s', err.messages)
            payload = {
                'success': False,
                'errors': err.messages,
                'msg': 'Erro de validação nos dados enviados',
                'error_type': type(err).__name__,
            }
            # incluir traceback em modo debug para facilitar o diagnóstico
            try:
                if current_app and getattr(current_app, 'debug', False):
                    payload['traceback'] = traceback.format_exc()
            except Exception:
                pass

            return payload

        except SQLAlchemyError as err:
            # erro no banco de dados
            logger.exception(
                'SQLAlchemyError ao tentar salvar novo utilizador')
            db.session.rollback()
            return {'success': False, 'msg': 'Erro ao salvar no banco de dados. Tente novamente.'}

        except Exception as e:
            # captura qualquer outra excepção inesperada
            db.session.rollback()
            # registar a exceção completa para debugging
            logger.exception('Erro interno em CadastrarService')
            # construir payload de erro consistente
            payload = {
                'success': False,
                'msg': 'Ocorreu um erro interno. Por favor, contacte o suporte.',
                'error': str(e),
                'error_type': type(e).__name__,
            }
            # incluir traceback completo apenas em ambiente de desenvolvimento
            try:
                if current_app and getattr(current_app, 'debug', False):
                    payload['traceback'] = traceback.format_exc()
            except Exception:
                # não falhar o handler de erro ao tentar ler current_app
                pass

            return payload


class LoginService:

    @staticmethod
    def autenticar(**dados: Dict[str, Any]):

        email = dados.get('email')
        senha = str(dados.get('senha'))
        lembrar: bool = bool(dados.get('lembrar', False))

        try:
            # Buscar utilizador pelo email
            user = db.session.query(Utilizador).filter_by(email=email).first()

            # validar utilizador e senha
            if user and user.verificar_senha(senha):

                # Fazer login e lembrar da sessão
                login_user(user, remember=lembrar)

                return {'success': True, 'msg': 'Login realizado com sucesso'}
            else:
                return {'success': False, 'msg': 'E-mail ou senha inválidos.'}

        except SQLAlchemyError as e:
            return {'success': False, 'msg': (e)}
