.. _plugins:

Using plugins
=============


Gru was built with the concept of extendability in mind. Since an inventory of hosts can have many different usages
and different companies have a different view of the world (also with regards to how their infrastructure is managed),
there's built-in support for 2 main types of plugins: *Host widgets* and *Page plugins*


.. _host-widgets:

Host Widgets
------------

Host Widgets are plugins that live within the context of a single host.

They are generally used to provide additional information about the host from external systems (say monitoring, configuration management, cost, etc)
or to support actions to be carried out for that host.


.. _page-plugins:

Page plugins
------------

Page plugins are plugins that transcend hosts in general. As their name suggests, they are pages that are rendered
within GRU and have access to the host inventory system. They are generally designed to complement GRU's use-cases
by adding more host/fleet related functionality.

For example, at SimilarWeb_, we built a page plugin that displays currently open incidents, linking back to relevant stacks and servers - which is used by on-call personnel.


.. _loading-plugins:

Loading plugins
---------------

In order to load an existing plugin, you'll need to do the following:


1. Make sure the plugin's python module is in gru's ``sys.path`` (python's search path for modules).

   The easiest way to accomplish this, is to either place the plugins under the default :ref:`plugin-directories`.

   Alternatively, you can specify your own directories to override the default paths.

2. For plugins that require configuration, see their documentation and update your GRU settings YAML file accordingly.

3. Restart the GRU web server for the changes to get picked up.



.. _SimilarWeb: http://www.similarweb.com/
