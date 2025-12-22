from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.historico.models import HistoricoAlteracaoPerfil, EventoHistorico
from app.pagamentos.models import Pagamento
from app.academia.models import Inscricao


def registar_alteracao_perfil(
    utilizador_id: int,
    motivo: str,
    perfil_antigo: Optional[str] = None,
    perfil_novo: Optional[str] = None,
    dados_extra: Optional[dict] = None,
) -> None:
    '''
    Regista uma alteração ou evento relacionado a um utilizador.

    Args:
        utilizador_id (int): ID do utilizador associado ao evento.
        motivo (str): Descrição breve do motivo do registo (ex.: 'Alteração de perfil').
        perfil_antigo (str, opcional): Perfil anterior do utilizador.
        perfil_novo (str, opcional): Novo perfil do utilizador.
        dados_extra (dict, opcional): Dados adicionais do evento (ex.: módulo, valores, etc).

    Uso:
        registar_alteracao(
            utilizador_id=current_user.id,
            motivo='Alteração de perfil',
            perfil_antigo='aluno',
            perfil_novo='cliente',
            dados_extra={'origem': 'auth', 'ip': request.remote_addr}
        )
    '''

    try:
        novo_registo = HistoricoAlteracaoPerfil(
            utilizador_id=utilizador_id,  # type: ignore
            motivo=motivo,  # type: ignore
            perfil_antigo=perfil_antigo,  # type: ignore
            perfil_novo=perfil_novo,  # type: ignore
            data_alteracao=datetime.now(timezone.utc),  # type: ignore
            dados_extra=dados_extra or {},  # type: ignore
        )

        db.session.add(novo_registo)
        db.session.commit()

    except SQLAlchemyError as e:
        db.session.rollback()

        print(f'[ERRO] Falha ao registar histórico: {e}')

    except Exception as e:
        db.session.rollback()

        # Futuramente deverá enviar logs para um serviço externo (ex.: Sentry)
        print(f'[ERRO] Falha ao registar histórico: {e}')


def get_historico_completo(utilizador_id):

    pagamentos = db.session.query(Pagamento).filter_by(
        utilizador_id=utilizador_id).all()
    inscricoes = db.session.query(Inscricao).filter_by(
        utilizador_id=utilizador_id).all()
    eventos = []

    for p in pagamentos:
        eventos.append(
            EventoHistorico(
                data=p.data_pagamento,
                tipo='pagamento',
                descricao=f'pagamento de {p.valor} kz via {p.metodo_pagamento}',
                valor=float(p.valor) if p.valor is not None else None))

    for i in inscricoes:
        descricao_turma = getattr(i.turma, 'nome', f'id:{i.turma}')
        eventos.append(
            EventoHistorico(
                data=i.data_inscricao,
                tipo='inscrição',
                descricao=f'inscrição na turma {descricao_turma}',
                valor=None
            )
        )

    eventos.sort(key=lambda e: e.data, reverse=True)
    return eventos
