.. _authentication:

Authentication and Authorization
================================

GRU supports pluggable authentication and authorization.

To make things simple, authorization is done via user groups: a plugin can configure an ``allowed_groups`` variable
that lists group names that have authorization to use the plugin.

Configuring an Authentication Backend
-------------------------------------

Configuring the Authentication backend is done via the ``authentication.backend`` and ``authentication.config`` configuration parameters.
Both are covered in the :ref:`configuration documentation <authentication-backend>`


Dummy authentication backend
----------------------------

By default, gru sets the authentication backend to ``gru.contrib.auth.backends.DummyBackend``.

This backend, as its name suggests, does nothing. No need for users to login, and users have no groups associated
with them.

If you use GRU in a network where only authorized personnel have access to the web interface, this might be enough.
Make sure you protect this network and that you don't accidentally expose it to the world.

For all other situations, it is recommended to use a real authentication backend such as the LDAP one described below.


LDAP authentication backend
---------------------------

The LDAP backend is used to authenticate users against an existing LDAP server (such as Active Directory or OpenLDAP).

Once a user has been authenticated, the LDAP backend also populates user's group names, to allow plugins to authorize
only users of specific groups.

To enable the LDAP backend, please use ``gru.contrib.auth.backends.LdapBackend`` as the value for ``authentication.backend``
and refer to the :ref:`backend documentation <config-params-ldap-backend>` for details on how to populate the ``authentication.config`` dictionary for the LDAP backend.

Here's a snippet of such a configuration:

.. code-block:: yaml

    ---
    authentication:
      backend: gru.contrib.auth.backends.LdapBackend
      config:
        server: 10.0.0.7
        port: 3268
        bind_user: 'CN=gru,OU=Internal Tools,DC=mycompany,DC=com'
        bind_password: '**************'
        user_query: '(sAMAccountName=$username)'


Writing your own
----------------

Writing an authentication backend is covered under :ref:`Writing your own authentication backends <plugin_dev_auth_backends>`


