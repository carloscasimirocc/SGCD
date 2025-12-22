import os
from flask_mailman import EmailMessage
from threading import Thread
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

# Importações da sua lógica de negócio
from app.extensions import db
from app.publico.models import Mensagem
from app.publico.schemas import MensagemSchema

# --- Funções Auxiliares de Envio ---


def enviar_email_assincrono(aplicacao, mensagem):
    """
    Função auxiliar para enviar e-mails de forma assíncrona.
    """
    with aplicacao.app_context():
        try:
            mensagem.send()
        except Exception as erro:
            aplicacao.logger.error(
                f"Falha no envio de e-mail assincrono: {erro}")


def enviar_email_mailman(destinatarios, assunto, modelo_corpo, **kwargs):
    """
    Função principal para enviar e-mails usando Flask-Mailman.
    """
    # 1. Obtém o objeto real da aplicação para passar para a thread
    aplicacao = current_app._get_current_object()

    # O remetente padrão é lido da configuração MAIL_DEFAULT_SENDER
    remetente = current_app.config.get('FLASKY_ADMIN')

    mensagem = EmailMessage(
        subject=assunto,
        body=modelo_corpo,
        to=destinatarios,
        from_email=remetente
    )

    # Inicia o envio numa thread separada
    thread = Thread(target=enviar_email_assincrono, args=[aplicacao, mensagem])
    thread.start()
    return thread

# --- Função de Notificação de Erro ---


def enviar_alerta_admin(assunto, corpo):
    """
    Envia um e-mail de alerta para o administrador da aplicação (FLASKY_ADMIN).
    """
    email_admin = current_app.config.get('FLASKY_ADMIN')

    if not email_admin:
        current_app.logger.error(
            "FLASKY_ADMIN não está configurado. Não é possível enviar alerta.")
        return

    assunto_completo = f"[ALERTA {current_app.name.upper()}] {assunto}"

    enviar_email_mailman(
        destinatarios=[email_admin],
        assunto=assunto_completo,
        modelo_corpo=corpo
    )

# --- Função de Orquestração Principal ---


def processar_mensagem_contacto(dados_formulario):
    """
    Orquestra o processamento de uma mensagem de contacto:
    1. Valida os dados (Schema).
    2. Regista na base de dados (Modelo Mensagem).
    3. Envia e-mail de confirmação ao cliente.
    4. Envia e-mail de notificação ao administrador.

    :param dados_formulario: Um dicionário com os dados do formulário (Nome, email, Conteudo).
    :return: True em caso de sucesso, False em caso de falha.
    """

    # 1. Validação dos Dados (Usando o Schema)
    try:
        schema = MensagemSchema()
        # O load() do Marshmallow valida e retorna um dicionário limpo
        dados_validados = schema.load(dados_formulario)

    except ValidationError as erro:
        # Erro de validação: registamos e retornamos False
        current_app.logger.error(
            f"Erro de validação do formulário de contacto: {erro.messages}")
        # Não enviamos alerta ao admin para erros de validação comuns
        return False

    # 2. Registo na Base de Dados (Usando o Modelo Mensagem)
    try:
        nova_mensagem = Mensagem(
            nome=dados_validados['nome'],  # type:ignore
            email=dados_validados['email'],  # type:ignore
            conteudo=dados_validados['conteudo']  # type:ignore
        )
        db.session.add(nova_mensagem)
        db.session.commit()
        current_app.logger.info(
            f"Mensagem de {dados_validados['email']} registada com sucesso.")

    except SQLAlchemyError as erro:
        # Erro de BD: fazemos rollback, registamos e alertamos o admin
        db.session.rollback()
        current_app.logger.error(f"Erro ao registar mensagem na BD: {erro}")
        enviar_alerta_admin("ERRO CRÍTICO: Falha no Registo de Mensagem",
                            f"Erro: {erro}\nDados: {dados_validados}")
        return False

    # 3. Envio de E-mail de Confirmação ao Cliente
    try:
        assunto_cliente = "Confirmação: Recebemos a sua mensagem - decifer.site"
        corpo_cliente = f"""
        Olá {dados_validados['nome']},

        Recebemos a sua mensagem e entraremos em contacto consigo o mais brevemente possível.

        Detalhes da sua mensagem:
        --------------------------
        {dados_validados['conteudo']}
        --------------------------

        Obrigado pelo seu contacto!
        A equipa decifer.site
        """

        enviar_email_mailman(
            destinatarios=[dados_validados['email']],  # type:ignore
            assunto=assunto_cliente,
            modelo_corpo=corpo_cliente
        )

    except Exception as erro:
        # Falha no envio de e-mail: registamos e retornamos False para notificar a rota
        current_app.logger.error(
            f"Falha ao enviar e-mail de confirmação ao cliente: {erro}")
        return False

    # 4. Envio de E-mail de Notificação ao Administrador
    try:
        assunto_admin = f"NOVA MENSAGEM de {dados_validados['nome']} ({dados_validados['email']})"
        corpo_admin = f"""
        Nova mensagem de contacto recebida:

        Nome: {dados_validados['nome']}
        Email: {dados_validados['email']}

        Conteúdo:
        --------------------------
        {dados_validados['conteudo']}
        --------------------------
        """

        enviar_alerta_admin(
            assunto=assunto_admin,
            corpo=corpo_admin
        )

    except Exception as erro:
        # Falha na notificação do admin: apenas registamos, não impede o sucesso do formulário
        current_app.logger.error(
            f"Falha ao enviar e-mail de notificação ao administrador: {erro}")

    return True
