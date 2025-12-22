import csv
from io import BytesIO
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from sqlalchemy import func, Integer
from app.extensions import db
from app.pagamentos.models import Pagamento
from app.academia.models import Inscricao


def get_total_por_mes(ano):
    query = db.session.query(Pagamento).with_entities(
        func.strftime('%Y-%m', Pagamento.data_pagamento)
        .label('mes'), func.sum(Pagamento.valor).label('total')
    )
    if ano is None:
        ano = datetime.now().year

    if ano:
        query = query.filter(func.strftime(
            '%Y', Pagamento.data_pagamento) == str(ano))

    resultados = query.group_by(
        'mes').order_by('mes').all()

    return [{'mes': mes, 'total': float(total)} for mes, total in resultados]


def get_resumo_estatistico(inicio, fim):

    query = db.session.query(Pagamento)

    if inicio:
        query = query.filter(Pagamento.data_pagamento >= inicio)

    if fim:
        query = query.filter(Pagamento.data_pagamento <= fim)

    total = query.with_entities(func.sum(Pagamento.valor)).scalar() or 0
    media = query.with_entities(func.avg(Pagamento.valor)).scalar() or 0
    menor = query.with_entities(func.min(Pagamento.valor)).scalar() or 0
    maior = query.with_entities(func.max(Pagamento.valor)).scalar() or 0

    return {'total': total,
            'media': media,
            'menor': menor,
            'maior': maior
            }


def get_total_por_trimestre(ano=None):

    query = db.session.query(Pagamento).with_entities(
        func.cast((func.strftime('%m', Pagamento.data_pagamento).cast(Integer)-1) /
                  3 + 1, Integer).label('trimestre'), func.sum(Pagamento.valor).label('total')
    )

    if ano:
        query = query.filter(func.strftime(
            '%Y', Pagamento.data_pagamento) == str(ano))

    resultados = query.group_by('trimestre').order_by('trimestre').all()

    return [{'trimestre': int(trim), 'total': float(total)} for trim, total in resultados]


def exportar_csv(inicio, fim):
    '''
    Exporta pagamentos do período selecionado para CSV.
    Retorna o conteúdo do ficheiro (em bytes).
    '''
    pagamentos = db.session.query(Pagamento).filter(
        Pagamento.data_pagamento >= inicio,
        Pagamento.data_pagamento <= fim
    ).all()

    output = BytesIO()
    writer = csv.writer(output)  # type: ignore
    writer.writerow(['Data', 'Valor (Kz)', 'Método', 'Descrição'])

    for p in pagamentos:
        writer.writerow([
            p.data_pagamento.strftime('%d/%m/%Y'),
            f'{p.valor:.2f}',
            p.metodo_pagamento,
            getattr(p, 'descricao', '')
        ])

    output.seek(0)
    return output.getvalue()


def exportar_pdf(inicio, fim):
    '''
    Exporta pagamentos do período selecionado para PDF.
    Usa ReportLab para gerar uma tabela simples.
    '''
    pagamentos = db.session.query(Pagamento).filter(
        Pagamento.data_pagamento >= inicio,
        Pagamento.data_pagamento <= fim
    ).all()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph('Relatório de Pagamentos', styles['Title']))
    elements.append(Paragraph(
        f'Período: {inicio.strftime('%d/%m/%Y')} — {fim.strftime('%d/%m/%Y')}', styles['Normal']))
    elements.append(Spacer(1, 12))

    data = [['Data', 'Valor (Kz)', 'Método', 'Descrição']]
    for p in pagamentos:
        data.append([
            p.data_pagamento.strftime('%d/%m/%Y'),
            f'{p.valor:.2f}',
            p.metodo_pagamento,
            getattr(p, 'descricao', '')
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
    ]))

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer
