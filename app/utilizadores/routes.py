from flask import Blueprint, request, flash, redirect, url_for, render_template, abort
from flask_login import login_required, current_user
from app.utilizadores.services import Utilizador
from app.utilizadores.models import PerfilEnum
from app.pagamentos.services import get_pag_por_utilizador, get_pag_recentes

utilizadores_bp = Blueprint(
    'utilizadores', __name__, template_folder='templates')


@utilizadores_bp.route('/alterar_perfil/<int:utilizador_id>', methods=['POST'])
@login_required
def alterar_perfil(utilizador_id):
    novo_perfil = request.form.get('perfil')
    sucesso = Utilizador.alterar_perfil(utilizador_id, PerfilEnum(
        novo_perfil), motivo='Alteração manual via painel')

    if sucesso:
        flash('Perfil alterado com sucesso!', 'success')
    else:
        flash('Erro ao alterar o perfil.', 'danger')

    return redirect(url_for('utilizadores.listar'))


@utilizadores_bp.route('/<int:id>/pagamentos')
@login_required
def listar_pagamentos(id):
    if current_user != id or not current_user.is_admin():
        abort(403)
    pagamentos = get_pag_por_utilizador(id)
    return render_template('utilizadores/pagamentos.html', pagamentos=pagamentos)


@utilizadores_bp.route('/<int:id>/painel')
@login_required
def painel_aluno(id):
    pagamentos_recentes = get_pag_recentes(id)
    return render_template('painel_aluno.html', pagamentos_recentes=pagamentos_recentes)
