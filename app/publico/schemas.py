from marshmallow import Schema, fields, validate, EXCLUDE


class MensagemSchema(Schema):

    nome = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    conteudo = fields.Str(required=True, validate=validate.Length(min=10))

    class Meta:
        unknown = EXCLUDE
