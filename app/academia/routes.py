'''
Rotas do módulo Academia — gestão de inscrições.

Responsabilidades:
- Expor endpoints REST que utilizam o service de inscrições
- Garantir respostas JSON consistentes
- Validar dados de entrada e status HTTP adequados
'''

from app.decorators import roles_required
from datetime import timezone, datetime
from flask import Blueprint
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from app.extensions import db


from app.academia.models import Inscricao, Turma
from app.academia.forms import CriarInscricaoForm, CancelarInscricaoForm, ConfirmarInscricaoForm, PresencaForm
from app.utilizadores.models import DadosAluno, Utilizador
from app.academia.services import criar_inscricao, confirmar_inscricao, cancelar_inscricao, registar_presenca

academia_bp = Blueprint('academia', __name__, template_folder='templates')


@academia_bp.route('/inscricao/criar', methods=['GET', 'POST'])
@login_required
def criar_inscricao_route():

    form = CriarInscricaoForm()

    if form.validate_on_submit():
        dados = {
            'aluno_id': form.aluno_id.data,
            'turma_id': form.turma_id.data
        }

        resultado = criar_inscricao(dados)

        if 'erro' in resultado:
            flash(resultado['erro'], 'danger')
        else:
            flash(resultado['mensagem'], 'success')

            # opcional: redirecionar para detalhes da inscrição ou lista
            return redirect(url_for('academia.criar_inscricao_route'))

    return render_template('academia/criar_inscricao.html', form=form, user=current_user)


@academia_bp.route('/inscricao/confirmar', methods=['GET', 'POST'])
@login_required
def confirmar_inscricao_route():

    form = ConfirmarInscricaoForm()

    if form.validate_on_submit():
        inscricao_id = form.inscricao_id.data
        inscricao_obj = db.session.query(Inscricao).get(inscricao_id)

        if not inscricao_obj:
            flash("Inscrição não encontrada.", "danger")
        else:
            resultado = confirmar_inscricao(inscricao_obj)

            if 'erro' in resultado:
                flash(resultado['erro'], 'danger')
            else:
                flash(resultado['mensagem'], 'success')
                return redirect(url_for('academia.confirmar_inscricao_route'))

    return render_template('academia/confirmar_inscricao.html', form=form, user=current_user)


@academia_bp.route('/inscricao/cancelar', methods=['GET', 'POST'])
@login_required
def cancelar_inscricao_route():

    form = CancelarInscricaoForm()

    if form.validate_on_submit():
        inscricao_id = form.inscricao_id.data
        inscricao_obj = db.session.query(Inscricao).get(inscricao_id)

        if not inscricao_obj:
            flash("Inscrição não encontrada.", "danger")
        else:
            resultado = cancelar_inscricao(inscricao_obj)

            if 'erro' in resultado:
                flash(resultado['erro'], 'danger')
            else:
                flash(resultado['mensagem'], 'success')
                return redirect(url_for('academia.cancelar_inscricao_route'))

    return render_template('academia/cancelar_inscricao.html', form=form,
                           user=current_user)


@academia_bp.route('/registar', methods=['GET', 'POST'])
@login_required
@roles_required('professor', 'administrador')
def registar_presenca_route():
    form = PresencaForm()

    # Preencher listas suspensas
    form.turma_id.choices = [(t.id, t.nome)
                             for t in db.session.query(Turma).all()]
    form.aluno_id.choices = [(a.id, a.utilizador.nome)
                             for a in db.session.query(DadosAluno).all()]

    if form.validate_on_submit():
        registar_presenca(
            data=datetime.now(timezone.utc),
            aluno_id=form.aluno_id.data,
            turma_id=form.turma_id.data,
            professor_id=current_user.id,
            presente=form.presente.data
        )
        flash('Presença registada com sucesso!', 'success')
        return redirect(url_for('presencas.registar_presenca_route'))

    return render_template('academia/registar_presenca.html', form=form)
