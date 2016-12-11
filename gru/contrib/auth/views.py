from flask import Blueprint, render_template, request, redirect, current_app


blueprint = Blueprint('auth', __name__)


@blueprint.route('/forbidden', methods=['GET'])
def forbidden_view():
    """
    A generic forbidden page to be shown when a user is not authorized to see a page
    """
    return render_template('auth/forbidden.html'), 401


@blueprint.route('/login', methods=['GET', 'POST'])
def login_view():
    """
    Login by calling the authenticator mounted on the Flask app.
    """
    template_name = 'auth/login.html'
    redirect_url = request.args.get('url')
    if not redirect_url:
        redirect_url = request.form.get('redir_url')
    ctx = {'redirect_url': redirect_url}
    if request.method == 'GET':
        return render_template(template_name, **ctx)
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        auth = current_app.plugins.authentication_backend
        user = auth.authenticate(username, password)
        if user is None:
            ctx.update({'error': 'Bad username / password'})
            return render_template(template_name, **ctx)
        current_app.plugins.authentication_backend.login(user)
        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect('/')


@blueprint.route('/logout', methods=['POST'])
def logout_view():
    """
    Logout by calling the authenticator mounted on the Flask app.
    This generally simply clears the session.
    """
    auth = current_app.plugins.authentication_backend
    auth.logout()
    redirect_url = request.args.get('url')
    if redirect_url:
        return redirect(redirect_url)
    else:
        return redirect('/')
