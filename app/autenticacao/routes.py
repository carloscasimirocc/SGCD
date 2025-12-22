from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, logout_user
from app.autenticacao.forms import FormCadastrar, FormLogin
from app.autenticacao.services import CadastrarService, LoginService


# criar blueprint
autenticacao_bp = Blueprint(
    'autenticacao', __name__, template_folder='templates')


@autenticacao_bp.route('/')
def index():
    return render_template('web_site.html', user=current_user)


@autenticacao_bp.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    form = FormCadastrar()

    if form.validate_on_submit():
        dados = form.data

        # validar os dados e registar no banco de dados usando o services
        resultado = CadastrarService.cadastrar(dados)

        if resultado['success'] == True:
            flash('parabéns, registo validado', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('relatorio.index'))
        else:
            # mostrar erros detalhados
            errors = resultado.get('errors')
            if errors:
                # flash each field error
                for field, msgs in errors.items():
                    for m in msgs:
                        flash(f"{field}: {m}", 'danger')
            else:
                flash(resultado['msg'], 'danger')
    else:
        # se houve POST mas validação WTForms falhou, mostrar erros do form
        if request.method == 'POST':
            # flash WTForms field errors to help debugging/user
            for field_name, field_errors in form.errors.items():
                for err in field_errors:
                    flash(f"{field_name}: {err}", 'danger')

    return render_template('cadastrar.html', form=form)


@autenticacao_bp.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('relatorio.index'))

    form = FormLogin()
    if form.validate_on_submit():
        resultado = LoginService.autenticar(**form.data)

        if resultado['success']:
            flash(resultado['msg'], 'success')
            return redirect(url_for('relatorio.index'))

        else:
            form.senha.errors = list(form.senha.errors) + [resultado['msg']]
            flash('email ou senhas errados ', 'warning')
            return render_template('login.html', form=form)

    return render_template('login.html', form=form)


@autenticacao_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sessão encerrada com sucesso!', 'success')
    return redirect(url_for('publico.desporto'))
