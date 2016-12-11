from string import Template

import simpleldap

from gru.plugins.base.auth import AuthenticationBackend, User
from gru.config import settings


class LdapBackend(AuthenticationBackend):
    """
    LDAP authentication backend.
    expects the following configuration in the inventory.yaml file
    under authentication.config:
        - server (string) - server IP or dns name
        - port (int) - port number
        - bind_user (string) - initial user name to connect to LDAP server
        - bind_password(string) - password for the initial user
        - user_query (string) - the LDAP query to make when searching for the user.
            Should contain a $username placeholder.
    """

    required_settings = [
        'authentication.config.server',
        'authentication.config.port',
        'authentication.config.bind_user',
        'authentication.config.bind_password',
        'authentication.config.user_query'
    ]

    @staticmethod
    def _split_ldap_spec(ldap_spec):
        return { k.split('=')[0]:k.split('=')[1] for k in ldap_spec.split(',') }

    def authenticate(self, username, password):
        server = settings.get('authentication.config.server')
        port = settings.get('authentication.config.port')
        bind_user = settings.get('authentication.config.bind_user')
        bind_password = settings.get('authentication.config.bind_password')
        query = Template(settings.get('authentication.config.user_query'))
        with simpleldap.Connection(server, port, bind_user, bind_password) as conn:
            try:
                user = conn.get(query.substitute(username=username))
            except simpleldap.ObjectNotFound:
                return None
        with simpleldap.Connection(server, port) as conn:
            if conn.authenticate(user.dn, password):
                return User(
                    username=username,
                    name=user.first('cn'),
                    groups=[self._split_ldap_spec(x)['CN'] for x in user.get('memberof', [])]
                )
        return None
