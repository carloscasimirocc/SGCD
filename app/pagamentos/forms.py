# app/pagamentos/forms.py
from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from app.pagamentos.models import TipoServicoEnum


class PagamentoForm(FlaskForm):
    valor = DecimalField(
        'Valor (Kwz)',
        validators=[DataRequired(), NumberRange(min=0.01)],
        places=2
    )

    tipo_servico = SelectField(
        'Tipo de Serviço',
        choices=[(t.name, t.value) for t in TipoServicoEnum],
        validators=[DataRequired()],
        coerce=str
    )

    metodo_pagamento = SelectField(
        'Método de Pagamento',
        choices=[
            ('dinheiro', 'Dinheiro'),
            ('transferencia', 'Transferência Bancária'),
            ('cartao', 'Cartão')
        ],
        validators=[DataRequired()]
    )

    observacoes = TextAreaField('Observações (opcional)')
    submit = SubmitField('Concluir Pagamento')
