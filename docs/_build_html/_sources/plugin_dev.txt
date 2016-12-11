.. _plugin_dev:

Developing Plugins
==================

To understand the basic concept of plugins and how to use them, refer to the :ref:`usage documentation <plugins>`

This document describes the process and APIs required to develop your own plugins.


.. _plugin_dev_arch:

Plugin Architecture Overview
----------------------------

GRU Plugins are Python classes that subclass abstract plugin classes.

For example, to write your own *Host Widget*, you'll need to subclass the :any:`gru.plugins.base.hostwidget.HostWidgetPlugin` class.

On startup, the server will do the following:


1. Add the directories listed under :ref:`plugin-directories` to Python's ``sys.path``

2. It will then iterate over the module names listed in ``plugins.modules`` and import them

3. For each imported module, the server will iterate over all classes, looking for ones that subclass any of GRU's internal abstract plugin types

4. An object will be instantiated out of each class found. The default ``on_load()`` method will be called. This is where plugin startup code should live. Things like setting up database connections should be done there

5. For modules that expose views_, a Flask Blueprint_ will be registered and used when serving these views


All plugins subclass the following abstract class:


.. py:class:: gru.plugins.base.BasePlugin

   .. py:method:: on_load(self):

      Defaults to doing nothing.
      If you have any startup logic, this is the place to put it.



.. _plugin_dev_widgets:

Host Widgets
------------

To write your own Host widget you'll need to provide the following:

1. A subclass of ``gru.plugins.base.hostwidget.HostWidgetPlugin``

2. A template file that extends ``plugins/host_widget.html``. This Jinja_ template defines 3 parts that you'll be able to overide. They will later be merged into the host info page. These parts are:
        - ``plugincss`` - will be loaded at the head of the host info page. This is where ``<style>`` or ``<link rel="...">`` tags should go.
        - ``pluginhtml`` - the actual HTML to be rendered inside the host info page body, under the basic host information
        - ``pluginjs`` - will be placed at the bottom of the HTML body. This is where ``<script>`` tags should go.

   All template blocks will get the results of the plugin class' ``get_context(self, host)`` method. That's probably the one you'll need to override.


Here's a reference of the plugin class:


.. py:class:: gru.plugins.base.hostwidget.HostWidgetPlugin

   .. py:attribute:: template_name

      A name of a template file to render. The file must extend ``plugins/host_widget.html`` and define the blocks listed above.

      You can define a ``templates/`` directory inside your module's parent directory. If it exists, GRU will add it to the template
      search path.

   .. py:method:: get_title(self):

      You must provide an implementation of this method.
      It should return a string that will be used as the title for this widget in the host info page.


   .. py:method:: qualify(self, host):

      Given a :any:`gru.plugins.inventory.Host` object, should return ``True`` or ``False``.
      If ``True``, the widget will be rendered for the given host's info page.

      This is useful If you have widgets that don't make sense for every host, so you want to display them
      only where appropriate.

   .. py:method:: def get_context(self, host):

      Given a :any:`gru.plugins.inventory.Host` object, should return a python dictionary to be used as context for the template file.
      The default implementation simply returns ``{}``, so you'll likely want to override it.

   .. py:method:: def ajax_request(self, request):

      Useful if you want the widget to be able to send AJAX requests back to  the server.
      The method will receive a Flask request object, and should return a valid `Flask response`_.



.. _plugin_dev_pages:

Page Plugins
------------

To write your own Page Plugin you'll need to provide the following:

1. A subclass of :any:`gru.plugins.base.page.PagePlugin`

2. Optionally, if this page plugin returns an HTML page to be rendered within GRU: A template file that extends ``plugins/page.html``. This Jinja_ template defines 3 parts that you'll be able to overide. They will later be merged into the host info page. These parts are:
        - ``plugincss`` - will be loaded at the head of the page. This is where ``<style>`` or ``<link rel="...">`` tags should go.
        - ``pluginhtml`` - the actual HTML to be rendered. GRU will wrap this with the default navbar, footer, etc.
        - ``pluginjs`` - will be placed at the bottom of the HTML body. This is where ``<script>`` tags should go.

3. If the plugin defines a ``get_title()`` method, it will be linked to from the navigation bar, in the ``plugins`` dropdown.


Here's a reference of the plugin class:


.. py:class:: gru.plugins.base.page.PagePlugin

   .. py:attribute:: template_name

      *Optional* - a name of a template file to render. The file must extend ``plugins/page.html`` and define the blocks listed above.

      You can define a ``templates/`` directory inside your module's parent directory. If it exists, GRU will add it to the template
      search path.

      You may also define a ``static/`` directory, containing static resources such as images, scripts and CSS files.
      To later include them within your template, use the ``plugin_static()`` function within your template. Example::

        <script src="{{plugin_static('myplugin/js/plugin.js')}}"></script>

      This will be replaced with the URL given to your ``static/myplugin/js/plugin.js`` file.

   .. py:method:: get_title(self):

      Should return a string. It will be used to register the plugin in the plugins dropdown, in GRU's navigation bar.
      The default implementation returns ``None`` meaning it won't be registered in the plugins dropdown.


   .. py:method:: handler(self, request):

      The method will receive a Flask request object, and should return a valid `Flask response`_.
      You may simply ``return self.render()`` here, which will render the template you provided using the ``template_name`` attribute.

      Sometimes it's useful to register a PagePlugin which returns a JSON response.
      Generally it will be called using an AJAX call by another plugin. In such a case,
      you should keep the default ``get_title(self)`` implementation and probably leave ``template_name`` blank as well.


   .. py:method:: render(self, http_status=200, **kwargs):

      A helper method that renders a Jinja template and return a `Flask response`_.
      Whatever you passed in as ``kwargs`` will be added to the Jinja_ context when rendering the template.

      The template to render will be taken from the ``template_name`` attribute.

.. _plugin_dev_inventory_providers:

Inventory Providers
-------------------

Writing an Inventory Provider requires subclassing :any:`gru.plugins.inventory.InventoryProvider`.

To use the plugin you developed, you'll need to make sure the module is loaded (specified under ``plugins.modules``) and
that ``inventory.provider`` points to your subclass' path.


.. py:class:: gru.plugins.inventory.InventoryProvider

   .. py:method:: host_group_breakdown(self, category):

      Returns a list of :any:`gru.plugins.inventory.HostCategory` objects.
      Example: if ``category = "datacenter"``, an expected return value would be ``[HostCategory("datacenter", "us-east-1", 10), HostCategory("datacenter", "us-west-2", 5)]``

   .. py:method:: list(self, category, group, sort_by=None, from_ind=None, to_ind=None):

      Returns a :any:`gru.plugins.inventory.HostList` object after filter by a field and value.
      Example: ``provider.list("datacenter", "us-east-1")`` will return all Hosts in the *us-east-1* datacenter

      Use ``from_ind`` and to_ind`` to support pagination. Both values are zero-based integers.

      ``sort_by`` is optional. If set, the list of :any:`gru.plugins.inventory.Host` objects should be sorted by this field name.

   .. py:method:: host_search(self, query, from_ind=None, to_ind=None):

      Given a query string, perform a search of hosts and returns a :any:`gru.plugins.inventory.HostList` object.

      ``query`` will be a string provided by the user in the search box.

      Use ``from_ind`` and to_ind`` to support pagination. Both values are zero-based integers.

   .. py:method:: get_host_by_id(self, host_id):

      Return a :any:`gru.plugins.inventory.Host` object for the provided host_id.


Host, HostCategory and HostList
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

------------


.. py:class:: gru.plugins.inventory.Host

   A ``Host`` is the most basic primitive in GRU. A host will generally have some unique ID (a MAC address, an AWS instance ID, or similar)
   and a key/value mapping of metadata. Common metadata attributes may include OS version, IP address, role, datacenter, etc.

   .. py:method:: __init__(self, host_id, host_data=None):

      Creates a new host by passing in a host identifier (should be unique) and a python dictionary describing host metadata information.

   .. py:method:: field(self, field_name, default=None):

      Returns a field value from the host metadata.

      Also supports fetching nested fields using ``"."`` notation. i.e. ``host.field('os.name')`` will work with this metadata: ``{'os': {'name': 'Linux'}``


------------


.. py:class:: gru.plugins.inventory.HostCategory

   Use this class when returning a list of host categories from the ``host_group_breakdown()`` method of a :any:`gru.plugins.inventory.InventoryProvider`.

   .. py:method:: __init__(self, category, group, count=0):

      ``category`` - a string specifying the category to breakdown by. e.g. ``"datacenter"``

      ``group`` - a string specifying the current group. e.g. ``"us-east-1"``

      ``count`` - an integer specifying the amount of hosts in the group. e.g. ``0``



------------


.. py:class:: gru.plugins.inventory.HostList

   This class represents a response to a search query or filter by an :any:`gru.plugins.inventory.InventoryProvider`.

   .. py:method:: __init__(self, hosts=None, total_hosts=0):

      ``hosts`` -a list of :any:`gru.plugins.inventory.Host` objects.

      ``total_hosts`` - integer. If the number passsed is bigger than ``len(hosts)``, a paginator will appear.




.. _plugin_dev_auth_backends:

Authentication Backends
-----------------------

Writing an Authentication Backend requires subclassing :any:`gru.plugins.auth.AuthenticationBackend`.

To use the plugin you developed, you'll need to make sure the module is loaded (specified under ``plugins.modules``) and
that ``authentication.backend`` points to your subclass' path.


.. py:class:: gru.plugins.auth.AuthenticationBackend

   .. py:method:: authenticate(self, username, password):

      Given a username and a password, should return a :any:`gru.plugins.auth.User` object if authentication is successful.

      Otherwise, return ``None``.

      *This is the only method an authentication backend has to implement.*

   .. py:method:: member_of(self):

      Will check which memebers the currently logged in user is a member of.
      If not logged in, will return an empty list.

   .. py:method:: is_logged_in(self):

      Returns True if there's a user currently logged in.

   .. py:method:: login(self, user):

      Stores the provided user object as part of the HTTP session

   .. py:method:: logout(self):

      Clears the current session.

   .. py:method:: get_forbidden_url(self):

      Returns a URL for a "Forbidden" page, in case a users tries a forbidden action

   .. py:method:: get_login_url(self, path):

      Returns a URL for the Login form page. If ``path`` is provided, it will be passed to the login page, which will redirect to it upon successful login.


The User object
~~~~~~~~~~~~~~~

.. py:class:: gru.plugins.auth.User

   Represents a logged in user. Has a username, real name, an optional list of groups and optional metadata

   .. py:method:: __init__(self, username, name, groups=None, user_data=None):

      Create a new user object. It will be serialized and stored as part of the session.

      ``username`` - The username used during authentication.

      ``name`` - The user's full name.

      ``groups`` - A list of strings describing the groups this user is a member of. Optional.

      ``user_data`` - A dictionary of additional metadata we want to store about this user. Optional.


.. _Blueprint: http://flask.pocoo.org/docs/latest/blueprints/
.. _Jinja: http://flask.pocoo.org/docs/latest/templating/
.. _Flask response: http://flask.pocoo.org/docs/latest/quickstart/#about-responses
.. _views: http://flask.pocoo.org/docs/0.11/views/#basic-principle
