from configparser import ConfigParser

from pepper.framework.di_container import singleton
from .api import Configuration, ConfigurationManager, ConfigurationContainer


class LocalConfigurationContainer(ConfigurationContainer):
    __config = None

    def load_configuration(self, config_file="config/pepper.config"):
        LocalConfigurationContainer.__config = ConfigParser()
        with open(config_file) as cfg:
            LocalConfigurationContainer.__config.read_file(cfg)

    @property
    @singleton
    def config_manager(self):
        if not LocalConfigurationContainer.__config:
            raise ValueError("No configuration loaded")

        return LocalConfigurationManager(LocalConfigurationContainer.__config)


class LocalConfigurationManager(ConfigurationManager):
    def __init__(self, config):
        self._config = config

    def get_config(self, name, callback=None):
        if callback:
            callback(LocalConfig(self._config, name))

        return LocalConfig(self._config, name)


class LocalConfig(Configuration):
    def __init__(self, parser, section):
        # type: (ConfigParser, str) -> None
        self._parser = parser
        self._section = section

    def get(self, key):
        return self._parser.get(self._section, key)

    def get_str(self, key):
        return str(self.get(key))

    def get_int(self, key):
        return self._parser.getint(self._section, key)

    def get_float(self, key):
        return self._parser.getfloat(self._section, key)

    def get_boolean(self, key):
        return self._parser.getboolean(self._section, key)

    def get_enum(self, key, type):
        return type[self.get_str(key).upper()]

    def __contains__(self, key):
        return self._parser.items(self._section).__contains__(key)

    def __iter__(self):
        return self._parser.items(self._section).__iter__()

    def __len__(self):
        return self._parser.items(self._section).__len__()
