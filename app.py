import os
import sys

from flask import Flask
from flask.ext.script import Manager
from flask.ext.seasurf import SeaSurf
from flask_collect import Collect

import gru.utils.web
import gru.utils.templates
import gru.utils.logs
import gru.utils.fs
from gru.config import settings
from gru.plugins.loader.registry import PluginRegistry
from gru.contrib.auth.sessions import ItsdangerousSessionInterface
from gru.contrib.auth.views import blueprint as auth_views
from gru.contrib.inventory.views import blueprint as inventory_views


def generate_app():
    app = Flask(
        __name__,
        template_folder=gru.utils.fs.relative_to(__file__, 'gru/templates'),
        static_folder=gru.utils.fs.relative_to(__file__, 'gru/static'))
    app.debug = settings.get('flask.debug')

    app.permanent_session_lifetime = settings.get('flask.session_seconds')

    # Client-side sessions with signed cookies
    app.secret_key = settings.get('flask.secret_key')
    app.session_interface = ItsdangerousSessionInterface()

    # Setup logging
    gru.utils.logs.setup_logging(app, settings)

    # CSRF protection
    SeaSurf(app)

    # Load sub-applications
    app.register_blueprint(auth_views, url_prefix='/auth')
    app.register_blueprint(inventory_views, url_prefix='/inventory')

    # Append plugin paths to sys.path
    for directory in settings.get('plugins.directories'):
        sys.path.append(os.path.abspath(os.path.expanduser(directory)))

    # Register plugins
    root_path = os.path.realpath(__file__)
    app.plugins = PluginRegistry(app, settings)
    for plugin_path in settings.get('plugins.modules'):
        app.plugins.register(plugin_path)

    # Also add authentication backend and inventory provider
    app.plugins.register(settings.get('authentication.backend'))
    app.plugins.register(settings.get('inventory.provider'))

    gru.utils.templates.setup(app)
    gru.utils.web.setup_base_views(app, settings)
    app.wsgi_app = gru.utils.web.method_rewrite_middleware(app.wsgi_app)

    return app


# Entry point.
app = generate_app()


if __name__ == '__main__':
    # Wrap the app in a Flask-Scripts manager
    manager = Manager(app)
    collect = Collect()
    collect.init_app(app)
    collect.init_script(manager)
    manager.run()
