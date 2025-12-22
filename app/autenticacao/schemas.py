from marshmallow import Schema, ValidationError, validates_schema, fields, pre_load, post_load, validate, EXCLUDE
from marshmallow.validate import Email, Length, OneOf
from sqlalchemy.sql.operators import regexp_match_op
from app.utilizadores.models import Especialidade, PerfilEnum


class CadastrarSchema(Schema):
    email = fields.Str(required=True, validate=Email(error='e-mail inválido'))
    senha = fields.Str(required=True, load_only=True,
                       validate=[Length(min=6, max=30,)])
    confirmar_senha = fields.Str(load_only=True)
    nome = fields.Str(required=True, validate=Length(max=100),)
    sobrenome = fields.Str(required=True, validate=Length(max=100))
    data_nascimento = fields.Date(required=False, format='%Y-%m-%d')
    telefone = fields.Str(required=True)
    perfil = fields.Str(load_default=PerfilEnum.cliente.value)

    @validates_schema
    def validar_senha(self, data, **kwargs):
        """Valida se senha e confirmar_senha são iguais.

        Marshmallow may call schema validators with extra keyword args
        (partial, many, unknown), portanto aceitamos **kwargs para
        evitar TypeError durante a execução do validador.
        """
        if data.get('senha') != data.get('confirmar_senha'):
            raise ValidationError(
                {'confirmar_senha': ['As senhas não coincidem']})

    class Meta:
        unknown = EXCLUDE

    @post_load
    def sanitize(self, data, **kwargs):
        """Sanitiza os dados depois do load:

        - remove campos usados apenas para validação (confirmar_senha)
        - normaliza o email (strip + lower)
        """
        # remover campo de confirmação de senha que só serve para validação
        data.pop('confirmar_senha', None)

        # normalizar email
        email = data.get('email')
        if isinstance(email, str):
            data['email'] = email.strip().lower()

        return data


class EditaPerfilSchema(Schema):
    nome = fields.Str(required=False, validate=Length(max=100))
    sobrenome = fields.Str(required=False, validate=Length(max=100))
    email = fields.Email(required=False, validate=Length(max=120))
    senha = fields.Str(required=False, validate=Length(min=6, max=30))
    data_nascimento = fields.Date(required=False, load_only=True)


class UtilizadorPublicSchema(Schema):
    email = fields.Email(dump_only=True)
    sobrenome = fields.Str(dump_only=True)
    telefone = fields.Str(dump_only=True)
    perfil = fields.Str(dump_only=True)


class PerfilSchema(CadastrarSchema):
    ROLE = None

    @pre_load
    def sel_perfil(self, data, **kwargs):
        if self.ROLE:
            data['perfil'] = self.ROLE
        return data


class AdministradorSchema(PerfilSchema):
    ROLE = PerfilEnum.administrador.value


class ProfessorSchema(PerfilSchema):
    ROLE = PerfilEnum.professor.value
    especialidade = fields.Str(required=True, validate=OneOf(
        [e.value for e in Especialidade], error='Especialidade inválida'))


class AlunoSchema(PerfilSchema):
    ROLE = PerfilEnum.aluno.value
    matricula = fields.Int(dump_only=True)
    # atenção que o curso está em outra coluna e haverá a necessidade de criar uma tabela cursos e fazer a ligação
    curso = fields.Str(required=True, validate=Length(max=100))


class ClienteSchema(PerfilSchema):
    ROLE = PerfilEnum.cliente.value


class EditarPerfilSchema(Schema):
    email = fields.Email(dump_only=True)
    fullname = fields.Str(dump_only=True)
    telefone = fields.Str(dump_only=True)
    perfil = fields.Str(dump_only=True)
