from click.testing import CliRunner
import click
from flask.cli import with_appcontext


@click.command('criar-admin')
@click.argument('nome')
@click.argument('sobrenome')
@click.argument('email')
@click.argument('telefone')
@click.argument('senha_hash')
@click.argument('data_nascimento')
@with_appcontext
def criar_admin(nome, sobrenome, email, telefone, senha_hash, data_nascimento):
    '''Cria o administrador inicial caso não haja'''

    from app.utilizadores.models import Utilizador, PerfilEnum
    from app.extensions import db
    from datetime import datetime

    # construir dicionário com chaves string para passar como kwargs
    admin = {
        'nome': nome,
        'sobrenome': sobrenome,
        'email': email,
        'telefone': telefone,
        'senha_hash': senha_hash,
        'data_nascimento': data_nascimento
    }
    admin['data_nascimento'] = datetime.strptime(data_nascimento, '%d-%m-%Y')

    try:
        user = db.session.query(Utilizador).filter_by(
            perfil=PerfilEnum.administrador).first()

        if not user:
            novo_admin = Utilizador(**admin)
            novo_admin.perfil = PerfilEnum.administrador
            novo_admin.definir_senha(senha_hash)

            db.session.add(novo_admin)
            db.session.commit()

            click.echo(f"Administrador {nome} criado com sucesso!")
            return

        click.echo('Já existe um administrador')
    except:
        db.session.rollback()
