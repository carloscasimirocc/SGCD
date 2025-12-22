from __future__ import annotations

from decimal import Decimal
from datetime import datetime, timezone
import enum
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Numeric, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import Base

if TYPE_CHECKING:
    from app.utilizadores.models import Utilizador


class TipoServicoEnum(str, enum.Enum):
    matricula = "matricula"
    mensalidade = "mensalidade"
    aluguer_campo = "aluguer_campo"
    hospedagem = "hospedagem"
    piscina_balneario = "piscina_balneario"


class Pagamento(Base):
    __tablename__ = "pagamentos"

    # importar no escopo da classe para evitar importação circular
    from app.utilizadores.models import Utilizador

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    utilizador_id: Mapped[int] = mapped_column(ForeignKey("utilizadores.id"))
    tipo_servico: Mapped[TipoServicoEnum] = mapped_column(
        Enum(TipoServicoEnum), nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    metodo_pagamento: Mapped[str] = mapped_column(String(50), nullable=False)
    data_pagamento: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc)
    )

    utilizador: Mapped['Utilizador'] = relationship(
        back_populates="pagamentos")

    def __repr__(self):
        return f"<Pagamento {self.tipo_servico} - {self.valor} USD>"
