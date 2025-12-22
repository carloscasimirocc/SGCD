'''
Serviço responsável pela gestão de inscrições e actualização
de perfis de alunos no módulo Academia.

Responsabilidades:
- Criar inscrições validadas
- Confirmar inscrições e promover utilizadores para 'aluno'
- Cancelar inscrições e reverter perfil, se aplicável
'''

from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from marshmallow import ValidationError
from typing import Dict

from app.extensions import db
from app.utilizadores.models import PerfilEnum, DadosAluno
from app.academia.models import Inscricao, Turma, Presenca
from app.academia.schemas import CriarInscricaoSchema


@contextmanager
def atomic_transaction():
    '''
    Context manager garante que qualquer operação dentro do bloco
    é atómica (tudo ou nada).

    Se ocorrer uma excepção, o rollback é feito automaticamente.
    '''

    try:
        yield  # executa o bloco dentro do 'with'
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise


def confirmar_inscricao(inscricao: Inscricao) -> Dict:
    '''
    confirma se inscrição e actualiza o perfil do utilizador
    para 'aluno', caso ainda não tenha esse perfil
    '''

    try:
        with atomic_transaction():
            inscricao.activo = True

            if inscricao.aluno.perfil != PerfilEnum.aluno:
                inscricao.aluno.perfil = PerfilEnum.aluno
                inscricao.aluno.activo = True

        return {'mensagem': 'Inscrição confirmada com sucesso.'}

    except SQLAlchemyError as e:
        return {'erro': f'Erro ao confirmar inscrição {e}'}


def cancelar_inscricao(inscricao: Inscricao) -> Dict:
    '''
    cancela a inscrição e reverte o perfil de aluno para cliente
    '''

    try:
        with atomic_transaction():
            inscricao.activo = False
            outras_activas = db.session.query(Inscricao).filter(
                Inscricao.aluno_id == inscricao.aluno_id, Inscricao.id != inscricao.id, Inscricao.activo == True).count()

            if outras_activas == 0:
                inscricao.aluno.perfil = PerfilEnum.cliente

        return {'mensagem': 'Inscrição cancelada com sucesso.'}

    except SQLAlchemyError as e:
        return {'erro': f'Erro ao cancelar inscrição: {str(e)}'}


def criar_inscricao(dados: Dict) -> Dict:
    schema = CriarInscricaoSchema()

    try:
        with atomic_transaction():

            # validação dos dados recebidos
            dados_validos = schema.load(dados)

            # verificar se a validação retornou um dicionário
            if not isinstance(dados_validos, dict):
                return {'erro': 'Dados inválidos retornados pelo schema.'}

            # pegar IDs do dicionário retornado pelo schema
            aluno_id = dados_validos['aluno_id']
            turma_id = dados_validos['turma_id']

            # consultar tabela Inscrição a existencia de aluno_id e turma_id

            inscricao_existente = db.session.query(Inscricao).filter_by(
                aluno_id=aluno_id, turma_id=turma_id).first()

            if inscricao_existente:
                return {'erro': 'Aluno já inscrito nessa turma'}

            # buscar objetos alunos e turma pelos seus id's

            aluno_obj = db.session.query(DadosAluno).get(aluno_id)
            turma_obj = db.session.query(Turma).get(turma_id)

            # verificar se aluno e turma já existem
            if not aluno_obj or not turma_obj:
                return {'erro': 'Aluno ou turma não encontrados.'}

            # criar instancia usando usando objectos
            nova_inscricao = Inscricao(
                aluno_id=aluno_obj.id,  # type: ignore
                turma_id=turma_obj.id,  # type: ignore
                activo=False  # type: ignore
            )

            db.session.add(nova_inscricao)

        return {
            'mensagem': 'Inscrição criada com sucesso.',
            'inscricao_id': nova_inscricao.id,
            'aluno': aluno_obj.nome,
            'turma': turma_obj.nome
        }

    except ValidationError as e:
        db.session.rollback()
        return {'erros': e.messages}

    except SQLAlchemyError as e:
        db.session.rollback()
        return {'erro': f'Erro ao criar inscrição: {str(e)}'}

    except Exception as e:
        db.session.rollback()
        return {'erro': f'erro inesperado {str(e)}'}


def registar_presenca(data, aluno_id, turma_id, professor_id, presente=True):
    '''Cria um novo registo de presença.'''
    nova_presenca = Presenca(
        data=data,
        aluno_id=aluno_id,
        turma_id=turma_id,
        professor_id=professor_id,
        presente=presente
    )
    db.session.add(nova_presenca)
    db.session.commit()
    return nova_presenca


def listar_presencas_por_turma(turma_id):
    '''Lista todas as presenças de uma turma.'''
    return db.session.query(Presenca).filter_by(turma_id=turma_id).order_by(Presenca.data.desc()).all()
