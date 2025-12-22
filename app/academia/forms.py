from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, HiddenField, SelectField, BooleanField
from wtforms.validators import DataRequired, NumberRange


class CriarInscricaoForm(FlaskForm):
    '''
    Formulário para criar uma inscrição de aluno numa turma.
    '''
    aluno_id = IntegerField(
        'ID do Aluno',
        validators=[DataRequired(message='Campo obrigatório'),
                    NumberRange(min=1, message='ID inválido')]
    )
    turma_id = IntegerField(
        'ID da Turma',
        validators=[DataRequired(message='Campo obrigatório'),
                    NumberRange(min=1, message='ID inválido')]
    )
    submit = SubmitField('Criar Inscrição')


class ConfirmarInscricaoForm(FlaskForm):
    '''
    Formulário para confirmar uma inscrição existente.
    '''
    inscricao_id = IntegerField(
        'ID da Inscrição',
        validators=[DataRequired(message='Campo obrigatório'),
                    NumberRange(min=1, message='ID inválido')]
    )
    submit = SubmitField('Confirmar Inscrição')


class CancelarInscricaoForm(FlaskForm):
    '''
    Formulário para cancelar uma inscrição existente.
    '''
    inscricao_id = IntegerField(
        'ID da Inscrição',
        validators=[DataRequired(message='Campo obrigatório'),
                    NumberRange(min=1, message='ID inválido')]
    )
    submit = SubmitField('Cancelar Inscrição')


class PresencaForm(FlaskForm):
    turma_id = SelectField('Turma', coerce=int, validators=[DataRequired()])
    aluno_id = SelectField('Aluno', coerce=int, validators=[DataRequired()])
    presente = BooleanField('Presente', default=True)
    submit = SubmitField('Registar Presença')
