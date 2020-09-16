from typing import Callable

from pepper import logger, CameraResolution
from pepper.framework.abstract.backend import AbstractBackend
from pepper.framework.backend.container import BackendContainer
from pepper.framework.backend.system import SystemCamera, SystemMicrophone, SystemTextToSpeech, \
    SystemMotion, SystemLed, SystemTablet
from pepper.framework.config.api import ConfigurationManager, ConfigurationContainer
from pepper.framework.di_container import singleton
from pepper.framework.event.api import EventBusContainer, EventBus
from pepper.framework.resource.api import ResourceContainer, ResourceManager
from pepper.framework.sensor.api import SensorContainer
from pepper.framework.sensor.asr import AbstractTranslator


class SystemBackendContainer(BackendContainer, SensorContainer, EventBusContainer, ResourceContainer, ConfigurationContainer):
    logger.info("Initialized SystemBackendContainer")

    @property
    @singleton
    def backend(self):
        return SystemBackend(self.translator, self.event_bus, self.resource_manager, self.config_manager)


class SystemBackend(AbstractBackend):
    def __init__(self, translator_factory, event_bus, resource_manager, configuration_manager):
        # type: (Callable[[str, str], AbstractTranslator], EventBus, ResourceManager, ConfigurationManager) -> None
        """
        Initialize the System Backend.

        Parameters
        ----------
        translator_factory : Callable[[str, str], AbstractTranslator]
            Callable that provides an :class:`AbstractTranslator` based on internal and application language
        event_bus : EventBus
        resource_manager : ResourceManager
        configuration_manager : ConfigurationManager
        """
        config = configuration_manager.get_config("pepper.framework.backend.system")
        application_language = config.get("application_language")
        internal_language = config.get("internal_language")
        camera_resolution = config.get_enum("camera_resolution", CameraResolution)
        camera_rate = config.get_int("camera_frame_rate")
        microphone_rate = config.get_int("microphone_sample_rate")
        microphone_channels = config.get_int("microphone_channels")

        translator = translator_factory(internal_language[:2], application_language[:2])

        super(SystemBackend, self).__init__(SystemCamera(camera_resolution, camera_rate, event_bus),
                                            SystemMicrophone(microphone_rate, microphone_channels, event_bus, resource_manager),
                                            SystemTextToSpeech(translator, application_language, resource_manager),
                                            SystemMotion(), SystemLed(), SystemTablet())
