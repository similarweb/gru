import flask
from . import BaseRenderingPlugin, PluginException


class HostWidgetPlugin(BaseRenderingPlugin):

    template_name = None

    def _request_handler(self, *args, **kwargs):
        res = super(HostWidgetPlugin, self)._request_handler(*args, **kwargs)
        if res:
            return res
        request = flask.request
        if request.is_xhr:
            return self.ajax_request(request)
        raise PluginException('Host Widget plugins can only receive JSON based AJAX requests')

    def qualify(self, host):
        return True

    def get_context(self, host):
        return {}

    def get_title(self):
        raise NotImplementedError('this is a mandatory method')

    def ajax_request(self, request):
        """
        Will be called when this widget receives an XHR request.
        :param request: the Flask request object
        :return: a valid Flask response
        """
        raise NotImplementedError('ajax_request() was not implemented')

    def _render_block(self, template, blockname, ctx=None):
        ctx = dict() if ctx is None else ctx
        template_block = template.blocks.get(blockname)
        if template_block is None:
            return ''
        return ''.join(template_block(template.new_context(ctx)))

    def _render_blocks(self, host):
        """
        file that extends "plugins/host_widget.html".
        Only the following blocks will get rendered:
        1. 'plugincss' - rendered at the <head> of the page
        2. 'pluginhtml' - rendered in the page itself
        3. 'pluginjs' - rendered near the bottom of the <body> element.
        """
        def plugin_static(filename):
            return flask.url_for(
                '{}.static',format(self.name),
                filename=filename)
        template_render_kwargs = {
            'plugin_name': self.name,
            'plugin_static': plugin_static,
            'title': self.get_title(),
            'host': host,
            'ajax_url': self.get_url(),
        }
        view_context = self.get_context(host)
        template_render_kwargs .update(view_context)
        tpl = flask.current_app.jinja_env.get_template(self.template_name)
        return {
            'js': self._render_block(tpl, 'pluginjs', template_render_kwargs),
            'css': self._render_block(tpl, 'plugincss', template_render_kwargs),
            'html': self._render_block(tpl, 'pluginhtml', template_render_kwargs),
            'title': self.get_title()
        }
