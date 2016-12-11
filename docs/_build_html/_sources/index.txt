.. _index:

Welcome to GRU's documentation!
===============================

What is GRU?
------------

GRU is a host-centric inventory management system. It is used to visualize and provide context on individual servers
and more importantly, on groups of servers.

It was designed in order to help operations teams, as well as developers to better understand their infrastructure
and to provide a unified view of available compute resources.

This is what it looks like:


.. figure:: gru_list.png
   :alt: GRU Host breakdown by role

   *GRU Host breakdown by role*


.. figure:: gru_host.png
   :alt: GRU Host info page

   *GRU Host info page*


Motivation
----------

Understanding which compute resources exist (and which business context they serve) can be tricky.
In many cases, this information is scattered across several systems.

GRU is designed to give an accurate view of compute resources available to us.
The main primitive in GRU is the **Host**. By providing different ways to slice and dice an inventory (or, collection of hosts)
and allowing plugins to give external context regarding each host, we can better discover, understand and optimize our infrastructure.

Plugins, that are at the center of GRU, are used to integrate information and actions from external systems.
These can include monitoring, CMDB, real time metrics, cost info, service checks and more.
By uniting all these into one place we can easily reason about our resources and provide visibility to operations and software engineers.



Contents:

.. toctree::
   :maxdepth: 2

   quickstart
   inventory
   authentication
   plugins
   plugin_dev
   configuration
   contributing
   roadmap
