from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TelField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, Regexp, ValidationError
from app.utilizadores.models import Utilizador
from app.extensions import db


def todas_minusculas(valor):
    return valor.lower() if valor else valor


def todas_maiusculas(valor):
    return valor.upper() if valor else valor


def eliminar_espaco(valor):
    return valor.strip() if valor else valor


def maiuscula_prim(valor):
    return valor.capitalize() if valor else valor


def espaco_entre_palavras(valor):
    return valor.replace(' ', '') if valor else valor


class FormCadastrar(FlaskForm):
    nome = StringField(label='Seu nome', validators=[DataRequired()], filters=[
                       eliminar_espaco, espaco_entre_palavras, todas_minusculas, maiuscula_prim])
    sobrenome = StringField(label='Seu sobrenome', validators=[
                            DataRequired()], filters=[eliminar_espaco, espaco_entre_palavras, maiuscula_prim])
    email = StringField(label='Seu e-mail',
                        validators=[DataRequired(), Email()], filters=[eliminar_espaco, todas_minusculas])
    senha = PasswordField(label='Senha',
                          validators=[
                              DataRequired(),
                              EqualTo('confirmar_senha', message=None),
                              Regexp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$',
                                     message='❌ senha têm de ter pelo menos seis carateres, 1 letra no mínimo e um número.')])
    confirmar_senha = PasswordField(label='Confirme a senha', validators=[
        DataRequired(), EqualTo('senha', message='Senhas devem ser iguais!')])

    telefone = TelField(label='Telefone',
                        validators=[DataRequired(),
                                    Regexp(r'^\+?\d{9,12}$',
                                    message='❌ Número de telefone inválido. Deve conter entre 9 e 12 dígitos, podendo começar com +')], filters=[eliminar_espaco])
    data_nascimento = DateField(
        label='Data de Nascimento', format='%Y-%m-%d', validators=[DataRequired(message='informe a data de nascimento')])
    enviar = SubmitField(label='Cadastrar')

    def validate_email(self, email):
        '''verifica se o email já existe no banco de dados'''
        utilizador_existente = db.session.query(Utilizador).filter_by(
            email=email.data.lower()).first()
        if utilizador_existente:
            raise ValidationError('email já existente')

    def validate_telefone(self, telefone):
        '''verifica se o telefone já existe no banco de dados'''
        telefone_existente = db.session.query(Utilizador).filter_by(
            telefone=telefone.data).first()
        if telefone_existente:
            raise ValidationError('Este número de telefone já está registado')


class FormLogin(FlaskForm):
    email = StringField(label='Seu e-mail',
                        validators=[DataRequired(), Email()])
    senha = PasswordField(label='Senha', validators=[DataRequired()])
    lembrar = BooleanField(label='Lembrar-me')
    enviar = SubmitField(label='Entrar')

    def validate_email(self, email):
        utilizador = db.session.query(
            Utilizador).filter_by(email=email.data).first()
        if not utilizador:
            raise ValidationError(
                'Usuário inexistente, crie uma conta')


class FormEditarPerfil(FlaskForm):
    nome = StringField(label='Seu nome', validators=[Optional()])
    sobrenome = StringField(label='Seu sobrenome', validators=[Optional()])
    email = StringField(label='Seu e-mail', validators=[Optional(), Email()])
    senha = PasswordField(label='Senha', validators=[Optional()])
    data_nascimento = StringField(
        label='Data de Nascimento', validators=[Optional()])
    editar = SubmitField(label='Editar')


class FormEditarPerfilAdmin(FlaskForm):
    email = StringField(
        label='Seu e-mail', validators=[Optional()], filters=[todas_minusculas, eliminar_espaco])
    telefone = TelField(label='Telefone', validators=[
                        Optional()], filters=[eliminar_espaco])
    nome = StringField(label='Seu nome', validators=[Optional()], filters=[
                       eliminar_espaco, maiuscula_prim])
    sobrenome = StringField(label='Seu sobrenome', validators=[
                            Optional()], filters=[eliminar_espaco, maiuscula_prim])
    num_bi = StringField(label='Nº Bi', validators=[
                         Optional()], filters=[eliminar_espaco, todas_maiusculas])
    telefone = TelField(label='Telefone', validators=[Optional()])
    data_nascimento = StringField(
        label='Data de Nascimento', validators=[Optional()])
