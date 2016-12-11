import os

import flask

from gru.config import settings


class PluginException(Exception):
    """
    Base class for plugin related exceptions.
    """
    pass


class PluginSettingsException(PluginException):
    """
    Raised when a plugin is not properly configured
    """
    pass


class BasePlugin(object):
    """
    A base class for all plugins. Most 3rd party plugins need to
    inherit from a subclases such as PagePlugin or HostWidget plugin.
    """

    # A list of strings describing mandatory settings that should exist
    #  in the config file.
    # If a setting is missing, startup will fail.
    required_settings = []

    def get_name(self):
        if hasattr(self, 'name'):
            return self.name
        return self.__class__.__name__

    def __init__(self, **kwargs):
        self.app = kwargs.get('app')
        self.kwargs = kwargs
        for required_setting in self.required_settings:
            if required_setting not in settings:
                raise PluginException(
                    '{} is a required setting for the {} plugin.'.format(
                        required_setting, self.get_name()))

    def on_load(self):
        pass  # A hook for startup logic


class BaseRenderingPlugin(BasePlugin):
    """
    Define logic for plugins that need templates
    and static files such as page plugins and Host Widget plugins.
    """

    path = ''

    def __init__(self, **kwargs):
        super(BaseRenderingPlugin, self).__init__(**kwargs)
        self.session = flask.session

    def _request_handler(self, *args, **kwargs):
        # This is overriden by other base classes such as
        # PageRenderingPlugin and HostWidgetPlugin
        authenticator = self.app.plugins.authentication_backend
        if not authenticator.is_logged_in():
            return flask.redirect(authenticator.get_login_url(flask.request.path))
        if len(self.allowed_groups) > 0 and len(list(set(self.allowed_groups) & set(authenticator.member_of()))) == 0:
            return flask.redirect(authenticator.get_forbidden_url())

    def get_title(self):
        raise NotImplementedError('this is a mandatory method')

    def allowed_methods(self):
        return ['GET']

    def get_url(self, **kwargs):
        module_name = os.path.basename(self.__class__.__module__)
        return flask.url_for('{}.{}'.format(module_name, self.get_name()), **kwargs)

    def send_json(self, http_status=200, **kwargs):
        return flask.jsonify(**kwargs), http_status

    def is_json_request(self, request):
        if request.is_xhr:
            return True
        best = request.accept_mimetypes \
            .best_match(['application/json', 'text/html'])
        return best == 'application/json' and \
            request.accept_mimetypes[best] > \
            request.accept_mimetypes['text/html']
