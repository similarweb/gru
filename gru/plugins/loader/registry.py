import os
import inspect

import flask
from werkzeug.utils import import_string

from gru.plugins.base import BasePlugin
from gru.plugins.base.page import PagePlugin
from gru.plugins.base.hostwidget import HostWidgetPlugin
from gru.plugins.base.auth import AuthenticationBackend
from gru.plugins.base.inventory import InventoryProvider


class PluginMetadata(object):

    def __init__(self, module_path, plugin_class_name, plugin_class):
        self.module_path = module_path
        self.plugin_class_name = plugin_class_name
        self.plugin_class = plugin_class

    def __repr__(self):
        return 'PluginMetadata(module_path="{}", plugin_class_name="{}", plugin_class={})'.format(
            self.module_path,
            self.plugin_class_name,
            self.plugin_class
        )


def subclasses(class_a, class_b):
    """
    Checks whether class_a is a subclass of class_b. Will also make sure it's not the same class
    :param class_a: Class to check
    :param class_b: Reference class to check against
    :return: True if A is an actual subclass of B
    """
    return issubclass(class_a, class_b) and class_a != class_b


class PluginRegistry(object):

    def __init__(self, app, settings):
        self.app = app
        self.settings = settings
        # Host widgets are a flat list of plugin instances
        self.host_widgets = []
        # Page plugins are rendered on their own seperate page
        self.pages = []
        # Holds the instantiated authentication backend that was chosen
        self.authentication_backend = None
        # Holds the inventory provider that was chosen
        self.inventory_provider = None

    def register(self, module_path):
        """
        Discover plugins under a given path
        i.e. "contrib.monitoring_overview".
        This looks for sub classes of the following:
            - PagePlugin
            - HostWidgetPlugin
            - AuthenticationBackend
            - InventoryBackend
            :param module_path: a string representing the python module to load
        """
        views = []
        plugin_instances = []
        module_ref = import_string(module_path)
        for attr_name in dir(module_ref):
            attr = getattr(module_ref, attr_name)
            try:
                if not subclasses(attr, BasePlugin):
                    continue  # Not a plugin
            except TypeError:
                continue  # Not a class
            plugin_path = '.'.join([module_path, attr_name])
            plugin = PluginMetadata(
                module_path,
                attr_name,
                attr)

            if subclasses(plugin.plugin_class, PagePlugin):
                views.append(plugin)

            elif subclasses(plugin.plugin_class, HostWidgetPlugin):
                views.append(plugin)

            elif subclasses(plugin.plugin_class, AuthenticationBackend) and \
                    plugin_path == self.settings.get('authentication.backend'):
                instance = self._get_instance(plugin)
                self.authentication_backend = instance
                plugin_instances.append(instance)

            elif subclasses(plugin.plugin_class, InventoryProvider) and \
                    plugin_path == self.settings.get('inventory.provider'):
                instance = self._get_instance(plugin)
                self.inventory_provider = instance
                plugin_instances.append(instance)

        # Create a blueprint and register it for all views in the plugin
        if views:
            view_instances = self._register_blueprint(module_path, module_ref, views)
            for view in view_instances:
                if isinstance(view, HostWidgetPlugin):
                    self.host_widgets.append(view)
                elif isinstance(view, PagePlugin):
                    self.pages.append(view)
            plugin_instances += view_instances

        # Run all startup hooks
        for plugin_instance in plugin_instances:
            plugin_instance.on_load()

    def _get_instance(self, plugin):
        """
        Returns an initialized instance of a plugin class, passing in the required arguments
        :param plugin: plugin class to initialize
        :return: instance of plugin
        """
        kwargs = {'app': self.app}
        return plugin.plugin_class(**kwargs)

    def _register_blueprint(self, module_path, module_ref, view_classes):
        module_name = os.path.basename(module_path).lower()
        module_blueprint = self._setup_blueprint(module_name, module_ref)
        instances = []
        for view_class in view_classes:
            view_instance = self._get_instance(view_class)
            module_blueprint.add_url_rule(
                view_instance.path,
                view_instance.get_name(),
                view_instance._request_handler,
                methods=view_instance.allowed_methods())
            instances.append(view_instance)
        self.app.register_blueprint(
            module_blueprint,
            url_prefix='/plugins/{}'.format(module_name))
        return instances

    def _setup_blueprint(self, module_name, module_ref):
        root_dir = os.path.dirname(inspect.getabsfile(module_ref))
        kwargs = {}
        # Register templates
        template_folder = os.path.join(root_dir, 'templates')
        if os.path.isdir(template_folder):
            kwargs.update({'template_folder': 'templates'})
        # Register static files, if any
        static_folder = os.path.join(root_dir, 'static')
        if os.path.isdir(static_folder):
            kwargs.update({
                'static_folder': 'static',
                'static_url_path': '/static/plugins/{}'.format(module_name)
            })

        # Generate blueprint
        blueprint = flask.Blueprint(module_name, module_name, **kwargs)

        # Add the plugin_static() helper function to the
        # template context
        @blueprint.context_processor
        def static_processor():
            def plugin_static(filename):
                return flask.url_for('{}.static'.format(module_name), filename=filename)
            return dict(plugin_static=plugin_static)

        # Blueprint done, return it
        return blueprint
