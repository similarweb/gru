.. _configuration:

Configuration Reference
=======================


Setting up a settings file
--------------------------

GRU is configured using a YAML settings file. see the :ref:`quickstart` guide to see how make sure GRU picks up
and uses the settings file we'll be providing.

At the most basic level, we need to let GRU know of the following:

1. Which inventory provider we want to use. EC2 and ElasticSearch come out of the box, but you can :ref:`write your own <plugin_dev>`.
2. Which authentication backend you want to use. Dummy (no auth at all) and LDAP authentication are provided, but, again, feel free to :ref:`write your own <plugin_dev>`.
3. How you want to display your inventory: Which metadata should be visible and where
4. Which external plugins you want to load, including any configuration they may require


Below is the full list of configuration parameters that GRU supports, including all the builtin plugins.
You can check out the ``examples/`` directory on Github_ for complete examples.

All basic configuration parameters
----------------------------------

For brevity, nested keys will be denoted using a period (``.``) i.e.:

.. code-block:: yaml

 foo.bar = <some value>

Is equivalent to the following YAML structure:

.. code-block:: yaml

 ---
 foo:
   bar: <some value>


``flask.debug``
**************
**boolean** whether to start the underlying flask server in debug mode or not. This will affect
the logging verbosity

``flask.secret_key``
********************
**string** used to encrypt signed cookies, used by the session system. Any random value will do.

``flask.session_seconds``
*************************
**integer** how long in seconds to keep user sessions.

Defaults to ``604800`` (7 days)

``ui.name``
***********
**string** name to use in the navbar and titles.

Defaults to ``GRU``.

``ui.items_per_page``
*********************
**integer** how many items to show on paginated pages.

Defaults to ``50``.

``ui.theme.name``
*****************
**string** name of the Bootswatch_ theme to use.

Defaults to ``darkly``.

``ui.theme.version``
********************
**string** Bootswatch_ theme version number.

Defaults to ``3.3.7``


.. _plugin-directories:

``plugins.directories``
***********************
**array of strings** list of directories that contain GRU plugins.

Defaults to ``['~/.gru-plugins', '/opt/gru-plugins']``

See :ref:`loading-plugins` for more info

``plugins.modules``
*******************
**array of strings** list of module names to import and search for plugins

See :ref:`loading-plugins` for more info


.. _authentication-backend:

``authentication.backend``
**************************
**string** class name for the authentication backend to use.

Out of the box, you can use either ``gru.contrib.auth.backends.LdapBackend`` or ``gru.contrib.auth.backends.DummyBackend``.


.. _inventory-provider:

``inventory.provider``
**********************
**string** class name of the inventory provider to use.

Out of the box, you can use either ``gru.contrib.inventory.providers.ElasticSearchProvider`` or ``gru.contrib.inventory.providers.EC2Provider``.

``inventory.group_by``
**********************
**array of dictionaries**

Describes the list of Host attributes to group the inventory by. This is used by the host breakdown screens.
Common fields to group hosts by may include: data center (or AWS region), environment, role and operating system.

Each dictionary should provide at least the ``field`` key, which corresponds to a Host attribute name, and an optional
``title`` key which will be used by the UI to give this field a human readable name.

Example:

.. code-block:: yaml

  ---
  inventory:
    group_by:
      - field: os
        title: Operating System
      - field: dc
        title: Data Center
      - field: role
    ...

This will appear in the UI under the "Browse Inventory" drop-down.

``inventory.host_display_name_field``
*************************************
**string**

A name for a Host attribute that will be used as the host's display name in various places in the UI.

Examples: ``"hostname"``, ``"instance-id"``


``inventory.host_table_sort_by``
********************************
**string**

A name for a Host attribute that will be used when sorting lists of hosts, on supporting Inventory Providers.
Out of the box, this is currently only supported by the ElasticSearch provider.

Examples: ``"hostname"``, ``"instance-id"``



``inventory.host_table_fields``
*******************************
**array of dictionaries**

Describe the list of Host attributes used when showing a table of multiple hosts.
Common fields will generally include: role, data center, OS, IP address, # of cores, memory GBs, etc.

Each dictionary should provide at least the ``field`` key, which corresponds to a Host attribute name, and an optional
``title`` key which will be used by the UI to give this field a human readable name.

Example:

.. code-block:: yaml

  ---
  inventory:
    host_table_fields:
      - field: os
        title: Operating System
      - field: dc
        title: Data Center
      - field: role
      - field: num_cores
        title: "# Of Cores"
      - field: memory_gb
        title: Memory GB
      - field: ipaddress
        title: IP address
    ...

The field names may vary depending on your Inventory Provider.


``inventory.host_info_fields``
******************************
**array of dictionaries**

Describe the list of Host attributes used when a single host. Other fields will be hidden behind a "show more..." button.
Common fields will generally include: role, data center, OS, IP address, # of cores, memory GBs, etc.

Each dictionary should provide at least the ``field`` key, which corresponds to a Host attribute name, and an optional
``title`` key which will be used by the UI to give this field a human readable name.

Example:

.. code-block:: yaml

  ---
  inventory:
    host_info_fields:
      - field: os
        title: Operating System
      - field: dc
        title: Data Center
      - field: role
      - field: num_cores
        title: "# Of Cores"
      - field: memory_gb
        title: Memory GB
      - field: ipaddress
        title: IP address
    ...

The field names may vary depending on your Inventory Provider.


.. _config-params-ldap-backend:

LDAP authentication backend configuration parameters
----------------------------------------------------

Here's what an LDAP configuration might look like:

.. code-block:: yaml

    authentication:
      backend: gru.contrib.auth.backends.LdapBackend
      config:
        server: 10.10.10.10
        port: 3268
        bind_user: 'CN=gru_bind_user,OU=ops,DC=example,DC=com'
        bind_password: 'binduserpassword'
        user_query: '(sAMAccountName=$username)'


``authentication.config.server``
********************************
**string**

LDAP server IP or hostname to use

``authentication.config.port``
********************************
**integer**

LDAP server port to use

``authentication.config.bind_user``
***********************************
**string**

LDAP user to bind with

``authentication.config.bind_password``
***************************************
**string**

LDAP password to bind with

``authentication.config.user_query``
************************************
**string**

LDAP query to perform when searching the logging in user.
You can use the ``$username`` interpolation token which will be replaced by the value provided by the logging in user.


.. _config-params-es-provider:

Configuration Parameters for the built-in ElasticSearch inventory provider
--------------------------------------------------------------------------

``inventory.config.index``
**************************
**string**

The ElasticSearch index name to use

``inventory.config.hosts``
**************************
**array of strings**

A list of urls to use when connecting to the ElasticSearch cluster.


``inventory.config.timeout_seconds``
**************************
**integer**

Amount of time in seconds before timing out a request to an ElasticSearch query

Defaults to ``30``.

.. _config-params-ec2-provider:

Configuration Parameters for the built-in EC2 inventory provider
----------------------------------------------------------------
``inventory.config.connections``
*************************************
**array of dictionaries**

Every connection to the EC2 API is represented by an entry in the connections array.

For each connection, specify the following:

``inventory.config.accounts`` - **array** the AWS accounts we want to connect to.

``inventory.config.accounts.[].aws_access_key_id`` - **string** *optional* the AWS access key ID to connect with. If omitted, it will be searched in your filesystem and environment variables in the `order listed in boto's documentation`_

``inventory.config.accounts.[].aws_secret_access_key`` - **string** *optional* the AWS secret access key to connect with. If omitted, it will be searched in your filesystem and environment variables in the `order listed in boto's documentation`_

``inventory.config.accounts.[].regions`` - **array of string** *optional* The AWS regions we wish to connect and pull inventory from. Example: ``['us-east-1', 'us-west-2']``

Example:

.. code-block:: yaml

    ---
    provider: gru.contrib.inventory.providers.EC2Provider
    config:
      accounts:
        - aws_access_key_id: AKXXXXXXXXXXXXXXXXXX
          aws_secret_access_key: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
          - regions: ['us-east-1', 'us-west-2']



.. _Github: http://www.github.com/similarweb/gru
.. _order listed in boto's documentation: http://boto3.readthedocs.io/en/latest/guide/configuration.html#configuring-credentials
.. _Bootswatch: https://bootswatch.com/
