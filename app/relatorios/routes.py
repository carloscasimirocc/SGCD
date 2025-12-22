from datetime import datetime
from flask import Blueprint, render_template, request, current_app
from flask_login import login_required, current_user

from app.relatorios.services import (
    get_total_por_mes,
    get_total_por_trimestre,
    get_resumo_estatistico,
)
from app.relatorios.schemas import (
    serialize_mensais,
    serialize_trimestrais,
    serialize_resumo,
)

relatorio_bp = Blueprint("relatorio", __name__, template_folder="templates")


@relatorio_bp.route('/')
@login_required
def index():
    return render_template('index.html')


@relatorio_bp.route("/perfil/<email>")
@login_required
def perfil(email):
    '''
    Exibe o painel de relatórios com filtros e gráficos.
    '''
    ano = request.args.get('ano', type=int, default=datetime.now().year)
    inicio_str = request.args.get('inicio')
    fim_str = request.args.get('fim')

    inicio = None
    fim = None
    try:
        inicio = datetime.fromisoformat(inicio_str) if inicio_str else None
    except ValueError:
        inicio = None
    try:
        fim = datetime.fromisoformat(fim_str) if fim_str else None
    except ValueError:
        fim = None

    raw_mensais = get_total_por_mes(ano)
    raw_trimestrais = get_total_por_trimestre(ano)
    raw_resumo = get_resumo_estatistico(inicio, fim)

    # lista [{'mes': int, 'total': float}, ...]
    por_mes = serialize_mensais(raw_mensais)
    por_trimestre = serialize_trimestrais(raw_trimestrais)
    resumo = serialize_resumo(raw_resumo)

    return render_template(
        'index.html'
    )
