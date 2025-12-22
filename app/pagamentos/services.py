from app.extensions import db
from app.utilizadores.models import PerfilEnum, Utilizador
from app.historico.services import registar_alteracao_perfil
from app.pagamentos.models import Pagamento, TipoServicoEnum
from typing import Optional
from decimal import Decimal


def processar_pagamento(utilizador_id: int, valor: Decimal, tipo_servico: str, metodo_pagamento: str, observacoes: Optional[str]):
    '''
    Processa o pagamento, regista histórico e atualiza o perfil do utilizador, se necessário.
    '''

    try:
        utilizador = db.session.get(Utilizador, utilizador_id)
        if not utilizador:
            return False, 'Utilizador não encontrado.'

        if tipo_servico not in TipoServicoEnum._member_names_:
            return False, 'Tipo de serviço inválido.'

        # Cria e grava o pagamento
        pagamento = Pagamento(
            utilizador_id=utilizador_id,  # type:ignore
            tipo_servico=TipoServicoEnum[tipo_servico.upper()],  # type:ignore
            valor=valor,  # type:ignore
            metodo_pagamento=metodo_pagamento,  # type:ignore
            observacoes=observacoes or None  # type:ignore
        )
        db.session.add(pagamento)

        # --- Atualização automática do perfil ---
        perfil_antigo = utilizador.perfil
        perfil_novo = perfil_antigo

        if tipo_servico == 'matricula' and utilizador.perfil == PerfilEnum.cliente:
            utilizador.perfil = PerfilEnum.aluno
            perfil_novo = PerfilEnum.aluno

        elif tipo_servico == 'cancelamento' and utilizador.perfil == PerfilEnum.aluno:
            utilizador.perfil = PerfilEnum.cliente
            perfil_novo = PerfilEnum.cliente

        db.session.commit()

        # Registo no histórico
        registar_alteracao_perfil(
            utilizador_id=utilizador.id,
            motivo=f'Pagamento de {tipo_servico}',
            perfil_antigo=perfil_antigo.value,
            perfil_novo=perfil_novo.value,
            dados_extra={
                'valor': valor,
                'metodo_pagamento': metodo_pagamento,
                'observacoes': observacoes
            }
        )

        return True, f'Pagamento de {tipo_servico} concluído com sucesso.'

    except Exception as e:
        db.session.rollback()
        return False, str(e)


def get_pag_por_utilizador(utilizador_id):
    lista_pagamentos = db.session.query(Pagamento).filter_by(utilizador_id=utilizador_id).order_by(
        Pagamento.data_pagamento.desc().all())
    return lista_pagamentos


def get_pag_recentes(utilizador_id, limite=5):
    pagamentos_recentes = db.session.query(Pagamento).filter_by(utilizador_id=utilizador_id).order_by(
        Pagamento.data_pagamento.desc().limit(limite).all())
    return pagamentos_recentes
