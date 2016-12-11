

DEFAULTS = {
    'flask.debug': True,
    'flask.session_seconds': 604800,

    'ui.name': 'GRU',
    'ui.items_per_page': 50,
    'ui.theme.name': 'darkly',
    'ui.theme.version': '3.3.7',

    'plugins.directories': ['~/.gru-plugins', '/opt/gru-plugins'],
    'plugins.modules': ['gru.contrib.auth.backends', 'gru.contrib.inventory.providers'],

    'authentication.backend': 'gru.contrib.auth.backends.DummyBackend',

    'inventory.host_display_name_field': 'hostname',
    'inventory.host_table_sort_by': 'hostname'
}