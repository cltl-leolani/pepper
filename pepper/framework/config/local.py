import os

from configparser import ConfigParser

import pepper
from pepper.framework.di_container import singleton
from .api import Configuration, ConfigurationManager, ConfigurationContainer

_CONFIG = "config/default.config"
_ADDITIONAL_CONFIGS = ["config/pepper.config", "config/credentials.config"]
_SECTION_ENVIRONMENT = "environment"


class LocalConfigurationContainer(ConfigurationContainer):
    # TODO Get rid of the need for the root_dir
    __config = ConfigParser({"root_dir": os.path.abspath(os.path.dirname(os.path.dirname(pepper.__file__)))}, strict=False)

    @staticmethod
    def load_configuration(config_file=_CONFIG, additional_config_files=_ADDITIONAL_CONFIGS):
        with open(config_file) as cfg:
            LocalConfigurationContainer.__config.read_file(cfg)
        LocalConfigurationContainer.__config.read(additional_config_files)

        if LocalConfigurationContainer.__config.has_section(_SECTION_ENVIRONMENT):
            for key, value in LocalConfigurationContainer.__config.items(_SECTION_ENVIRONMENT):
                os.environ[key] = value

    @staticmethod
    def get_config(name, key):
        return LocalConfigurationContainer.__config.get(name, key)

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
