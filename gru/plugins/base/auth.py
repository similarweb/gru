import urllib
from flask import session, url_for

from . import BasePlugin


class User(object):
    """
    User model
    AuthenticationBackend plugins should return an instance of this from their authenticate() metdods
    """

    def __init__(self, username, name, groups=None, user_data=None):
        self.username = username
        self.name = name
        if groups:
            self.groups = groups
        else:
            self.groups = []
        if user_data:
            self.user_data = user_data
        else:
            self.user_data = {}

    def __repr__(self):
        return 'User(username="{}", name="{}", groups={}, user_data={})'.format(
            self.username,
            self.name,
            self.groups,
            self.user_data
        )

    def as_json(self):
        return {
            'username': self.username,
            'name': self.name,
            'groups': self.groups,
            'user_data': self.user_data
        }

    @classmethod
    def from_session(cls):
        if 'user' not in session.keys():
            return None
        user_data = session.get('user')
        return cls(**user_data)


class AuthenticationBackend(BasePlugin):

    """
    All authentication backends should subclass this.
    only one important method to override:
    authenticate(username, password) -> returns either a user details
        dictionary containing a 'username' key and possibly other info
        or - return None in case authentication failed.
    """

    def authenticate(self, username, password):
        """
        Override me!
        """
        raise NotImplementedError()

    def member_of(self):
        user = User.from_session()
        if user:
            return user.groups
        return []

    def is_logged_in(self):
        user = User.from_session()
        if user:
            return True
        return False

    def login(self, user):
        session['user'] = user.as_json()

    def logout(self):
        session.clear()

    def get_forbidden_url(self):
        return url_for('auth.forbidden_view')

    def get_login_url(self, path):
        base = url_for('auth.login_view')
        if path:
            return '{}?{}'.format(base, urllib.urlencode({'url': path}))
        else:
            return base
