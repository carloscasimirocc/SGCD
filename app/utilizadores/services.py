from typing import Optional
from app.extensions import db
from app.utilizadores.models import Utilizador, PerfilEnum
from app.historico.services import registar_alteracao_perfil


def alterar_perfil(
        utilizador_id: int,
        novo_perfil: PerfilEnum,
        motivo: Optional[str] = None) -> bool:
    '''
    Altera o perfil de um utilizador e regista o histórico da alteração.

    Args:
        utilizador_id (int): ID do utilizador.
        novo_perfil (PerfilEnum): Novo perfil que o utilizador deve assumir.
        motivo (str, opcional): Motivo da alteração (ex.: 'Conclusão de curso').

    Returns:
        bool: True se alteração for bem-sucedida, False caso contrário.
    '''
    try:
        utilizador = db.session.get(Utilizador, utilizador_id)
        if not utilizador:
            print(f'[ERRO] Utilizador {utilizador_id} não encontrado.')
            return False

        perfil_antigo = utilizador.perfil
        utilizador.perfil = novo_perfil

        db.session.commit()

        # Regista no histórico a alteração do perfil
        registar_alteracao_perfil(
            utilizador_id=utilizador.id,
            motivo=motivo or f'Mudança de perfil de {perfil_antigo.value} para {novo_perfil.value}',
            perfil_antigo=perfil_antigo.value,
            perfil_novo=novo_perfil.value,
            dados_extra={
                'modulo': 'utilizadores',
                'acao': 'alterar_perfil'
            }
        )

        print(
            f'[INFO] Perfil do utilizador {utilizador.email} alterado para {novo_perfil.value}')
        return True

    except Exception as e:
        db.session.rollback()
        print(f'[ERRO] Falha ao alterar perfil: {e}')
        return False
