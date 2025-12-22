from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass

from sqlalchemy import ForeignKey, String, DateTime, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.extensions import Base


if TYPE_CHECKING:
    from app.utilizadores.models import Utilizador


class HistoricoAlteracaoPerfil(Base):
    '''
    Regista todas as alterações de perfil e outras ações relevantes
    feitas por um utilizador ou sobre um utilizador.
    '''

    __tablename__ = 'historico_alteracoes'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    utilizador_id: Mapped[int] = mapped_column(
        ForeignKey('utilizadores.id'), nullable=False)
    motivo: Mapped[str] = mapped_column(String(255), nullable=False)
    data_alteracao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    perfil_antigo: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True)
    perfil_novo: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True)
    dados_extra: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Exemplo de dados_extra: {'modulo': 'aluguer', 'id_reserva': 87, 'valor': 250.0}

    utilizador: Mapped['Utilizador'] = relationship(
        'Utilizador', back_populates='historico_perfis', lazy='joined')

    def __repr__(self):
        return (
            f'<HistoricoAlteracao utilizador={self.utilizador_id}'
            f'motivo={self.motivo} data={self.data_alteracao}>')


@dataclass
class EventoHistorico():
    data: datetime
    tipo: str
    descricao: str
    valor: float | None = None
