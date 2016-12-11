import os
import yaml

from .defaults import DEFAULTS


class ConfigMissingException(Exception):
    pass


class Settings():
    """
    Manage a YAML configuration file.
    This class does the file lookup (envvars, directory structure)
    and loading the YAML.
    """

    def __init__(self, yaml_path=None):
        self.yaml_path = self._find_yaml_path(yaml_path)
        self.config = self._parse()

    @staticmethod
    def _find_yaml_path(yaml_path=None):
        # First try an explict path
        if yaml_path is not None:
            return yaml_path
        # Fallback to searching an environment variable
        settings_file = os.environ.get('GRU_SETTINGS', 'gru_settings.yaml')
        return os.path.expanduser(settings_file)

    def _parse(self):
        path = self.yaml_path
        with open(path, 'r') as yaml_f:
            return yaml.load(yaml_f)

    def get(self, path, default=None, raises_exception=False):
        """
        returns a key from the YAML file.
        :param path: the path in the config file to return. May be a nested value with '.' as a delimiter
        :param default: a default value to return if the path does not contain a value
        :param raises_exception: set this to True to raise a `ConfigMissingException` exception instead of returning
            a default value when a path is not found.
        :returns: The configuration value for the given path
        """
        parts = path.split('.')
        curr_level = self.config
        if default is None and path in DEFAULTS:
            default = DEFAULTS.get(path)
        try:
            for part in parts:
                curr_level = curr_level[part]
        except (KeyError, AttributeError):
            if raises_exception:
                raise ConfigMissingException('setting "{}" not found'.format(path))
            return default
        return curr_level

    def __contains__(self, item):
        try:
            self.get(item, raises_exception=True)
            return True
        except ConfigMissingException:
            return False


# Initialize a global settings object
settings = Settings()
