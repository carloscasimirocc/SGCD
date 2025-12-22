from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class ContactoForm(FlaskForm):
    nome = StringField('Nome', validators=[
                       DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    conteudo = TextAreaField('Mensagem', validators=[
                             DataRequired(), Length(min=10)])
    submit = SubmitField('Enviar')
