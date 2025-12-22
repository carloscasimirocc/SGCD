from datetime import date
from typing import Optional
from extensions import db
from app.hotel.models import Quarto, ReservaHotel


def listar_quartos_disponiveis():
    '''Retorna todos os quartos marcados como disponíveis.'''
    return db.session.query(Quarto).filter_by(disponivel=True).all()


def criar_reserva(cliente_id, quarto_id, checkin, checkout) -> Optional[ReservaHotel]:
    '''Cria uma reserva e marca o quarto como indisponível.'''
    quarto = db.session.get(Quarto, quarto_id)
    if not quarto or not quarto.disponivel:
        return None

    dias = (checkout - checkin).days
    total = dias * quarto.preco_diaria

    reserva = ReservaHotel()
    reserva.cliente_id = cliente_id
    reserva.quarto_id = quarto_id
    reserva.data_checkin = checkin
    reserva.data_checkout = checkout
    reserva.total = total

    db.session.add(reserva)
    quarto.disponivel = False

    db.session.commit()
    return reserva
