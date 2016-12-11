from flask import session

from gru.plugins.base.auth import AuthenticationBackend, User


class DummyBackend(AuthenticationBackend):
    """
    Will always accept any user without validating a password
    """

    def authenticate(self, username, password):
        return User(username='', name='Guest')

    def is_logged_in(self):
        user = User(username='', name='Guest')
        session['user'] = user.as_json()
        return True

    def logout(self):
        pass

    def member_of(self):
        return []
