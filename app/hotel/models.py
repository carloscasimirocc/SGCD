from __future__ import annotations
from datetime import datetime, timezone
from decimal import Decimal
from extensions import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Enum, Boolean, DECIMAL, DATE, ForeignKey, Numeric
import enum


class TipoQuarto(enum.Enum):
    standard = 'standard'
    suite = 'suite'
    luxo = 'luxo'


class Quarto(Base):
    '''Tabela que representa os quartos disponíveis no hotel.'''
    __tablename__ = 'quartos'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    numero: Mapped[str] = mapped_column(
        String(10), unique=True, nullable=False)
    tipo: Mapped[TipoQuarto] = mapped_column(Enum(TipoQuarto), nullable=False)
    preco_diaria: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False)
    capacidade: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    disponivel: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False)

    reservas: Mapped['ReservaHotel'] = relationship(
        'ReservaHotel', back_populates='quarto')

    def __repr__(self):
        return f'<Quarto {self.numero} - {self.tipo}>'


class ReservaHotel(Base):
    '''Tabela de reservas realizadas pelos clientes.'''
    __tablename__ = 'reservas_hotel'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    cliente_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('utilizadores.id'), nullable=False)
    quarto_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('quartos.id'), nullable=False)
    data_checkin: Mapped[datetime] = mapped_column(DATE, nullable=False)
    data_checkout: Mapped[datetime] = mapped_column(DATE, nullable=False)
    total: Mapped[Decimal] = mapped_column(DECIMAL, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DATE, default=datetime.now(timezone.utc))

    quarto = relationship('Quarto', back_populates='reservas')

    def __repr__(self):
        return f'<Reserva {self.id} - Cliente {self.cliente_id}>'
