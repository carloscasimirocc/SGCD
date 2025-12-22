from marshmallow import Schema, fields


class CriarInscricaoSchema(Schema):
    '''
    Schema de validação para a inscricao
    '''

    aluno_id = fields.Int(required=True)
    turma_id = fields.Int(required=True)


class PresencaSchema(Schema):
    '''
    Schema de validação para a registar a Presença do aluno
    '''
    id = fields.Int(dump_only=True)
    data = fields.Date()
    presente = fields.Bool(required=True)
    aluno_id = fields.Int(required=True)
    turma_id = fields.Int(required=True)
    professor_id = fields.Int(required=True)
