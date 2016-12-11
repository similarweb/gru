import flask
from gru.plugins.base import BaseRenderingPlugin


class PagePlugin(BaseRenderingPlugin):

    # Auth: which groups are visible to which groups
    allowed_groups = []

    def get_title(self):
        """
        If overriden and a string is returned, it will be used to link to this page
            from the Plugins drop-down.
        :return: None for internal pages (API calls, etc) or a string describing this plugin's name.
        """
        return None

    def _request_handler(self, *args, **kwargs):
        res = super(PagePlugin, self)._request_handler(*args, **kwargs)
        if res:
            return res
        return self.handler(flask.request)

    def handler(self, request):
        raise NotImplementedError('this is a mandatory method')

    def render(self, http_status=200, **kwargs):
        kwargs.update({
            'plugin_name': self.get_name(),
            'plugin_url': self.get_url(),
            'title': self.get_title()
        })
        return flask.render_template(
            self.template_name, **kwargs), http_status

