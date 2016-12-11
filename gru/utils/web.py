import os
import flask

from werkzeug.urls import url_decode


def setup_base_views(app, settings):
    @app.route('/favicon.ico')
    def favicon():
        return flask.send_from_directory(
            os.path.join(app.root_path, 'static'),
            'favicon.png', mimetype='image/png')

    # Add settings to the context of all templates
    @app.context_processor
    def add_settings():
        return dict(settings=settings, app=app)

    # Main entrypoint
    @app.route('/')
    def index_page():
        # Find main category
        first_group = settings.get('inventory.group_by')[0]
        field = first_group.get('field')
        main_url = flask.url_for('inventory.group_breakdown', group=field)
        return flask.redirect(main_url)

    @app.before_request
    def before_request():
        method = flask.request.form.get('_method', '').upper()
        if method:
            flask.request.environ['REQUEST_METHOD'] = method
            ctx = flask._request_ctx_stack.top
            ctx.url_adapter.default_method = method
            app.logger.info("method: %s", flask.request.method)
            assert flask.request.method == method


def method_rewrite_middleware(app, input_name='__METHOD_OVERRIDE__'):
    allowed_methods = frozenset(('GET', 'POST', 'PUT', 'DELETE'))

    def _middleware(environ, start_response):
        query_string = environ.get('QUERY_STRING', '')

        if input_name in query_string:
            args = url_decode(query_string)
            method = args.get(input_name)

            if method in allowed_methods:
                environ['REQUEST_METHOD'] = method

        return app(environ, start_response)

    return _middleware
