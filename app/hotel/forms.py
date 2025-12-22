from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, SubmitField
from wtforms.validators import DataRequired


class ReservaHotelForm(FlaskForm):
    quarto = SelectField('Quarto', coerce=int, validators=[DataRequired()])
    data_checkin = DateField(
        'Data de Check-in', format='%Y-%m-%d', validators=[DataRequired()])
    data_checkout = DateField(
        'Data de Check-out', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Confirmar Reserva')
