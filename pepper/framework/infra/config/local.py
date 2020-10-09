import os

from configparser import ConfigParser

import pepper
from pepper.framework.infra.di_container import singleton
from .api import Configuration, ConfigurationManager, ConfigurationContainer

_DELIMITER = ","

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
                # items(section) includes also all entries from the default section
                if key not in LocalConfigurationContainer.__config.defaults():
                    # keys are converted to lower case by ConfigParser
                    os.environ[key.upper()] = value

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

    def get(self, key, multi=False):
        # TODO Python 3 Cast to string (instead of unicode string)
        val = str(self._parser.get(self._section, key))

        return val if not multi else [v.strip() for v in val.split(_DELIMITER)]

    def get_int(self, key):
        return self._parser.getint(self._section, key)

    def get_float(self, key):
        return self._parser.getfloat(self._section, key)

    def get_boolean(self, key):
        return self._parser.getboolean(self._section, key)

    def get_enum(self, key, type, multi=False):
        value = self.get(key, multi)
        string_values = value if multi else [value]
        enum_vals = [type[val.strip().upper()] for val in string_values]

        return enum_vals if multi else enum_vals[0]

    def __contains__(self, key):
        return self._parser.items(self._section).__contains__(key)

    def __iter__(self):
        return self._parser.items(self._section).__iter__()

    def __len__(self):
        return self._parser.items(self._section).__len__()
