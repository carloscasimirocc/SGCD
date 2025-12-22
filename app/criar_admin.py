from datetime import datetime
from app.app import create_app
from app.extensions import db
from app.utilizadores.models import Utilizador, DadosAdministrador, PerfilEnum

app = create_app()
with app.app_context():
    existente = db.session.query(Utilizador).filter_by(
        perfil=PerfilEnum.administrador).first()
    if existente:
        print("Já existe um administrador")
    else:
        dados = {
            'nome': 'Carlos',
            'sobrenome': 'Casimiro',
            'email': 'carloscasimirocc@gmail.com',
            'telefone': '923564101',
            'perfil': PerfilEnum.administrador,
            'data_nascimento': datetime.strptime('28-07-1986', '%d-%m-%Y')
        }
        senha = '12345a'

        novo = Utilizador(**dados)
        novo.definir_senha(senha)
        # associar o objecto DadosAdministrador — com cascade isto insere ambas as linhas
        novo.dados_admin = DadosAdministrador()

        try:
            db.session.add(novo)
            db.session.commit()
            print(f"Administrador {novo.nome} criado com sucesso")
        except Exception as e:
            db.session.rollback()
            print("erro ao criar administrador:", e)
