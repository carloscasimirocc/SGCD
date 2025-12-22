from flask import Blueprint, abort, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.pagamentos.forms import PagamentoForm
from app.pagamentos.services import processar_pagamento
from app.utilizadores.models import Utilizador
from app.extensions import db


pagamentos_bp = Blueprint('pagamentos', __name__)


@pagamentos_bp.route('/<int:id>/novo', methods=['GET', 'POST'])
@login_required
def novo_pagamento(id):

    utilizador = db.get_or_404(Utilizador, id)

    if current_user.id != utilizador.id and not current_user.is_admin():
        abort(403)

    form = PagamentoForm()
    if form.validate_on_submit():

        valor_raw = form.valor.data

        if valor_raw is None or isinstance(valor_raw, str):
            flash('Valor inválido ou em branco.', 'danger')
            return render_template('pagamento_form.html', form=form)

        sucesso, mensagem = processar_pagamento(
            utilizador_id=utilizador.id,
            valor=valor_raw,
            tipo_servico=form.tipo_servico.data,
            metodo_pagamento=form.metodo_pagamento.data,
            observacoes=form.observacoes.data
        )

        flash(mensagem, 'success' if sucesso else 'danger')
        if sucesso:
            return redirect(url_for('pagamentos.ver_pagamentos', id=utilizador.id))
    else:
        flash('Por favor, verifique os dados do formulário.', 'warning')

    return render_template('pagamento_novo.html', form=form, utilizador=utilizador)
