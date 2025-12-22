from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from .models import Quarto, ReservaHotel
from .forms import ReservaHotelForm
from .schemas import ReservaHotelSchema
from datetime import date
from typing import Optional
from sqlalchemy import text

hotel_bp = Blueprint('hotel', __name__, url_prefix='/hotel',
                     template_folder='templates')


@hotel_bp.route('/')
@login_required
def index():
    '''Lista os quartos disponíveis'''
    quartos = db.query(Quarto).filter_by(disponivel=True).all()
    return render_template('hotel/index.html', quartos=quartos)


@hotel_bp.route('/reservar/<int:quarto_id>', methods=['GET', 'POST'])
@login_required
def reservar(quarto_id):
    '''Formulário de reserva de quarto'''
    quarto = db.get_or_404(Quarto, quarto_id)
    form = ReservaHotelForm()

    # GET -> mostrar form
    if not form.validate_on_submit():
        return render_template('hotel/reserva.html', form=form, quarto=quarto)

    # POST e validado pelo WTForms
    inicio: Optional[date] = form.data_checkin.data
    fim: Optional[date] = form.data_checkout.data

    if inicio is None or fim is None:
        flash('Datas inválidas.', 'danger')
        return render_template('hotel/reserva.html', form=form, quarto=quarto)

    noites = (fim - inicio).days
    if noites <= 0:
        flash('A data de checkout deve ser posterior à data de checkin.', 'danger')
        return render_template('hotel/reserva.html', form=form, quarto=quarto)

    # Re-verificar disponibilidade atual do quarto e criar reserva de forma atómica
    total = quarto.preco_diaria * noites
    data = {
        'cliente_id': current_user.id,
        'quarto_id': quarto.id,
        'data_checkin': inicio,
        'data_checkout': fim,
        'total': total
    }

    schema = ReservaHotelSchema()
    try:
        schema.load(data)
    except Exception as err:
        flash(f'Erro de validação: {err}', 'danger')
        return render_template('hotel/reserva.html', form=form, quarto=quarto)

    try:
        # Para SQLite: força lock de escrita imediato para evitar condição de corrida
        bind = db.session.get_bind() if hasattr(
            db.session, "get_bind") else getattr(db.session, "bind", None)

        if bind is not None and getattr(bind, "dialect", None) is not None and bind.dialect.name == "sqlite":
            db.session.execute(text("BEGIN IMMEDIATE"))

        # obter o quarto dentro da transacção/session atual
        quarto_db = db.session.get(Quarto, quarto_id)
        if not quarto_db or not quarto_db.disponivel:
            # se começou uma transacção manual, rollback
            db.session.rollback()
            flash('O quarto já não está disponível.', 'warning')
            return redirect(url_for('hotel.index'))

        # criar reserva e marcar quarto como indisponível dentro da mesma transacção
        reserva = ReservaHotel(**data)
        quarto_db.disponivel = False
        db.session.add(reserva)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        flash('Erro ao salvar reserva. Tente novamente.', 'danger')
        return render_template('hotel/reserva.html', form=form, quarto=quarto)

    flash('Reserva efetuada com sucesso!', 'success')
    return redirect(url_for('hotel.index'))
