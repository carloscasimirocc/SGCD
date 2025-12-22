# modules/hotel/schemas.py
from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from datetime import date


class QuartoSchema(Schema):
    id = fields.Int(dump_only=True)
    numero = fields.Str(required=True)
    tipo = fields.Str(required=True, validate=validate.Length(min=3))
    preco_diaria = fields.Float(required=True)
    capacidade = fields.Int(required=True)
    disponivel = fields.Bool()


class ReservaHotelSchema(Schema):
    id = fields.Int(dump_only=True)
    cliente_id = fields.Int(required=True)
    quarto_id = fields.Int(required=True)
    data_checkin = fields.Date(required=True)
    data_checkout = fields.Date(required=True)
    total = fields.Float(required=True)
    criado_em = fields.DateTime(dump_only=True)

    @validates_schema
    def validar_datas(self, data, **kwargs):
        """Valida se as datas são coerentes"""
        checkin = data.get('data_checkin')
        checkout = data.get('data_checkout')
        if checkin and checkout and checkin >= checkout:
            raise ValidationError(
                "Data de check-out deve ser posterior ao check-in.")
        if checkin and checkin < date.today():
            raise ValidationError(
                "Data de check-in não pode ser anterior a hoje.")
