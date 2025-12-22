from flask import Blueprint, render_template, url_for, request, redirect, flash
from flask_login import current_user
from app.publico.forms import ContactoForm
from app.publico.services import processar_mensagem_contacto

publico_bp = Blueprint(
    'publico', __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/publico/static'
)


@publico_bp.route('/')
def index():
    '''Página inicial pública.'''
    return render_template('index.html')


@publico_bp.route('/desporto')
def desporto():
    return render_template('desporto.html')


@publico_bp.route('/reservar-hotel', methods=['GET', 'POST'])
def reservar_hotel():
    '''Mostrar formulário de reserva para utilizadores autenticados.

    - GET: exibe o template `reservar_hotel.html`. Se o visitante não estiver
      autenticado, o template mostrará uma mensagem e um link para login.
    - POST: processa submissão (placeholder). Se o visitante não estiver
      autenticado redireciona para o login com `next`.
    '''

    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('Faça login para efetuar uma reserva.', 'warning')
            return redirect(url_for('autenticacao.login', next=request.path))

        # Aqui processarias os dados do formulário e criarias a reserva.

        # Por agora mostramos um placeholder e redirecionamos ao index.
        flash('Pedido de reserva recebido (funcionalidade em desenvolvimento).', 'success')
        return redirect(url_for('publico.index'))

    return render_template('reservar_hotel.html')


@publico_bp.route('/hotel')
def hotel():
    return render_template('hotel.html')


@publico_bp.route('/restaurante')
def restaurante():
    return render_template('restaurante.html')


@publico_bp.route('/sobre')
def sobre():
    return render_template('sobre.html')


@publico_bp.route('/eventos')
def eventos():
    return render_template('eventos.html')


@publico_bp.route('/contactos', methods=['GET', 'POST'])
def contactos():
    form = ContactoForm()
    if form.validate_on_submit():

        try:
            email_sucesso = processar_mensagem_contacto(request.form)

            if email_sucesso:
                flash(
                    'Mensagem enviada com sucesso! Receberá um e-mail de confirmação.', 'success')
                return redirect(url_for('publico.desporto'))
            else:
                # A mensagem foi guardada, mas o e-mail falhou
                flash('Mensagem enviada, mas houve um erro ao enviar o e-mail de confirmação. Por favor, contacte-nos directamente.', 'warning')
                return redirect(url_for('home.index'))

        except Exception as e:
            # Erro na validação ou na DB
            flash(f'Ocorreu um erro: {e}', 'danger')
            return redirect(url_for('publico.home'))

    return render_template('contactos.html', form=form)
