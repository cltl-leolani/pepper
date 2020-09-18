import enum
from typing import Iterable, Callable, Type

from pepper.framework.di_container import DIContainer


class ConfigurationContainer(DIContainer):
    @property
    def config_manager(self):
        # type: () -> ConfigurationManager
        raise ValueError("No ConfigurationManager configured")


class ConfigurationManager(object):
    """
    ConfigurationManager provides configurations available in the system.

    :class:`Configurations` are key-value mappings and provided by
    configuration name.
    """

    def get_config(self, name, callback=None):
        # type: (str, Callable[[Configuration], None]) -> Configuration
        """
        Obtain the :class:`Configuration` for the specified name.

        Parameters
        ----------
        name : str
            The name identifying the configuration.
        callback : Callable[(Configuration), None]
            Callback function that is called on configuration changes.

        Returns
        -------
        :class:`Configuration`
            The Configuration for the provided configuration name.

        Raises
        ------
        :class:`ValueError`
            If there is not Configuration with the given name
        """
        raise NotImplementedError()


class Configuration(object):
    def get(self, key, multi=False):
        # type: (str) -> object
        """
        Get a configuration value as String for the specified key.

        Parameters
        ----------
        key : str
            The key for the configuration value to be retrieved.
        multi : bool
            Retrieve a list of values if True, else a single value

        Returns
        -------
        str or Iterable[str]
            The configuration value, or a list of value if multi is True

        Raises
        ------
        :class:`KeyError`
            If there is no value configured for the specified key.
        """
        raise NotImplementedError()

    def get_int(self, key):
        # type: (str) -> int
        """
        A convenience method which coerces the configuration value for the
        specified key to an integer.

        Parameters
        ----------
        key : str
            The key for the configuration value to be retrieved

        Returns
        -------
        int
            The configuration value as int

        Raises
        ------
        :class:`ValueError`
            If the requested value cannot be coerced into a int value.
        :class:`KeyError`
            If there is no value configured for the specified key.
        """
        raise NotImplementedError()

    def get_float(self, key):
        # type: (str) -> float
        """
        A convenience method which coerces the configuration value for the
        specified key to a floating point number.

        Parameters
        ----------
        key : str
            The key for the configuration value to be retrieved.

        Returns
        -------
        float
            The configuration value as float

        Raises
        ------
        :class:`ValueError`
            If the requested value cannot be coerced into a floating point
            value.
        :class:`KeyError`
            If there is no value configured for the provided key.
        """
        raise NotImplementedError()

    def get_boolean(self, key):
        # type: (str) -> bool
        """
        A convenience method which coerces the configuration value for the
        specified key to a Boolean value. Note that the accepted values for the
        option are "1", "yes", "true", and "on", which cause this method to
        return True, and "0", "no", "false", and "off", which cause it to
        return False. These string values are checked in a case-insensitive
        manner. Any other value will cause it to raise ValueError.

        Parameters
        ----------
        key : str
            The key for the configuration value to be retrieved.

        Returns
        -------
        bool
            The configuration value as boolean

        Raises
        ------
        :class:`ValueError`
            If the requested value cannot be coerced into a boolean
            value.
        :class:`KeyError`
            If there is no value configured for the provided key.
        """
        raise NotImplementedError()

    def get_enum(self, key, type, multi=False):
        # type: (str, Type[enum.Enum]) -> Union[object, list[object]]
        """
        A convenience method which coerces the configuration value for the
        specified key to an :class:`enum.Enum` instance.

        Parameters
        ----------
        key : str
            The key for the configuration value to be retrieved.
        type :
            The type of :class:`enum.Enum` to be resolved from the
            configuration value.
        multi : bool
            Retrieve a list of values if True

        Returns
        -------
        Enum or Iterable[Enum]
            The configuration value as :class:`enum.Enum` instance, or a list
            of values if multi is True

        Raises
        ------
        :class:`ValueError`
            If the requested value cannot be coerced into an Enum instance for
            the specified Enum type.
        :class:`KeyError`
            If there is no value configured for the provided key.
        """
        raise NotImplementedError()

    def __getitem__(self, key):
        # type: (str) -> object
        """
        Get the configuration value for the specified key.

        Parameters
        ----------
        key : str
            The key of the configuration value to be retrieved.

        Returns
        -------
        object
            The value configured for the specified key.

        Raises
        ------
        :class:`KeyError`
            If there is no Configuration with the specified key.
        """
        return self.get(key)

    def __contains__(self, key):
        # type: (str) -> bool
        """
        Check if the Configuration contains the specified key.

        Parameters
        ----------
        key : str
            The key.

        Returns
        -------
        bool
            If the the Configuration contains the specified key.
        """
        raise NotImplementedError()

    def __iter__(self):
        # type: () -> Iterable[(str, object)]
        """
        Returns
        -------
        Iterable[(str, object)]
            Iterable over the key-value pairs in the configuration.
        """
        raise NotImplementedError()

    def __len__(self):
        # type: () -> int
        """
        Returns
        -------
        int
            The number of keys in the Configuration.
        """
        raise NotImplementedError()