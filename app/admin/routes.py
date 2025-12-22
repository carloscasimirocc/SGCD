from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.admin.services import AdminUserService
from app.admin.forms import EditarUtilizadorForm
from app.admin.services import admin_required
from app.relatorios.services import get_resumo_estatistico, get_total_por_mes
from app.extensions import db

admin_bp = Blueprint('administrador', __name__, template_folder='templates')


@admin_bp.route('/listar_utilizadores')
@admin_required
def listar_utilizadores():
    form = EditarUtilizadorForm()
    utilizadores = AdminUserService.listar_utilizadores()
    return render_template('listar_utilizadores.html', utilizadores=utilizadores, form=form)


@admin_bp.route('/editar_utilizador/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def editar_utilizador(user_id):
    user = db.session.query(AdminUserService).get(user_id)
    if not user:
        flash('Utilizador não encontrado', 'danger')
        return redirect(url_for('administrador.listar_utilizadores'))

    form = EditarUtilizadorForm(user)
    if form.validate_on_submit():
        user.nome = form.nome.data
        user.email = form.email.data
        # ... outros campos ...
        db.session.commit()
        flash('Utilizador atualizado com sucesso!', 'success')
        return redirect(url_for('administrador.listar_utilizadores'))
    return render_template('editar_utilizador.html', form=form, user=user)


@admin_bp.route('/remover_utilizador/<int:user_id>', methods=['POST'])
@admin_required
def remover_utilizador(user_id):
    if AdminUserService.remover_utilizador(user_id):
        flash('Utilizador removido!', 'success')
    else:
        flash('Utilizador não encontrado.', 'danger')
    return redirect(url_for('administrador.listar_utilizadores'))


@admin_bp.route('/relatorios')
@admin_required
def relatorios_admin():
    '''
    Página de relatórios do painel do administrador.
    Mostra estatísticas e gráfico de pagamentos mensais.
    '''
    # Define o período para o resumo (últimos 30 dias)
    fim = datetime.now()
    inicio = fim - timedelta(days=30)
    ano = datetime.now().year
    resumo = get_resumo_estatistico(inicio=inicio, fim=fim)
    grafico_dados = get_total_por_mes(ano)

    # Prepara dados do gráfico em formato de lista
    labels = [m['mes'] for m in grafico_dados]
    valores = [m['total'] for m in grafico_dados]

    return render_template(
        'admin/relatorios.html',
        resumo=resumo,
        labels=labels,
        valores=valores
    )
