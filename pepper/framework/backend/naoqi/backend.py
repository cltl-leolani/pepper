import logging

import qi
from naoqi import ALProxy
from typing import Callable

from pepper import CameraResolution, NAOqiMicrophoneIndex
from pepper.framework.backend.abstract.backend import AbstractBackend
from pepper.framework.backend.container import BackendContainer
from pepper.framework.backend.naoqi import NAOqiCamera, NAOqiMicrophone, NAOqiTextToSpeech, \
    NAOqiMotion, NAOqiLed, NAOqiTablet
from pepper.framework.backend.system import SystemCamera, SystemMicrophone, SystemTextToSpeech
from pepper.framework.config.api import ConfigurationManager, ConfigurationContainer
from pepper.framework.di_container import singleton
from pepper.framework.event.api import EventBusContainer, EventBus
from pepper.framework.resource.api import ResourceContainer, ResourceManager
from pepper.framework.sensor.api import SensorContainer
from pepper.framework.sensor.asr import AbstractTranslator

logger = logging.getLogger(__name__)


class NAOqiBackendContainer(BackendContainer, SensorContainer, EventBusContainer, ResourceContainer, ConfigurationContainer):
    logger.info("Initialized NAOqiBackendContainer")

    @property
    @singleton
    def backend(self):
        return NAOqiBackend(self.translator, self.event_bus, self.resource_manager, self.config_manager)


class NAOqiBackend(AbstractBackend):
    def __init__(self, translator_factory, event_bus, resource_manager, configuration_manager):
        # type: (Callable[[str, str], AbstractTranslator], EventBus, ResourceManager, ConfigurationManager) -> None
        """
        Initialize the NAOqi Backend.

        Parameters
        ----------
        translator_factory : Callable[[str, str], AbstractTranslator]
            Callable that provides an :class:`AbstractTranslator` based on internal and application language
        event_bus :
        resource_manager :
        configuration_mananger :

        See Also
        --------
        http://doc.aldebaran.com/2-5/index_dev_guide.html
        """
        config = configuration_manager.get_config("pepper.framework.backend.naoqi")
        ip = config.get("ip")
        port = config.get_int("port")
        application_language = config.get("application_language")
        internal_language = config.get("internal_language")
        camera_resolution = config.get_enum("camera_resolution", CameraResolution)
        camera_frame_rate = config.get_int("camera_frame_rate")
        microphone_index = config.get_enum("microphone_index", NAOqiMicrophoneIndex)
        microphone_rate = config.get_int("microphone_sample_rate")
        microphone_channels = config.get_int("microphone_channels")
        speech_speed = config.get_int("speech_speed")
        use_system_camera = config.get_boolean("use_system_camera")
        use_system_microphone = config.get_boolean("use_system_microphone")
        use_system_text_to_speech = config.get_boolean("use_system_text_to_speech")

        self._url = config.get("url")

        # Create Session with NAOqi Robot
        self._session = self.create_session(self._url)

        # System Camera Override
        if use_system_camera:
            camera = SystemCamera(camera_resolution, camera_frame_rate, event_bus)
        else:
            camera = NAOqiCamera(self.session, camera_resolution, camera_frame_rate, event_bus)

        # System Microphone Override
        if use_system_microphone:
            microphone = SystemMicrophone(microphone_rate, microphone_channels, event_bus, resource_manager)
        else:
            microphone = NAOqiMicrophone(self.session, microphone_rate, microphone_index, event_bus, resource_manager)

        # System Text To Speech Override
        if use_system_text_to_speech:
            translator = translator_factory(internal_language[:2], application_language[:2])
            text_to_speech = SystemTextToSpeech(translator, application_language, resource_manager)
        else:
            text_to_speech = NAOqiTextToSpeech(self.session, application_language, speech_speed, resource_manager)

        # Set Default Awareness Behaviour
        self._awareness = ALProxy("ALBasicAwareness", ip, port)
        self._awareness.setEngagementMode("SemiEngaged")
        self._awareness.setStimulusDetectionEnabled("People", True)
        self._awareness.setStimulusDetectionEnabled("Movement", True)
        self._awareness.setStimulusDetectionEnabled("Sound", True)
        self._awareness.setEnabled(True)

        super(NAOqiBackend, self).__init__(camera, microphone, text_to_speech,
                                           NAOqiMotion(self.session, event_bus),
                                           NAOqiLed(self.session, event_bus),
                                           NAOqiTablet(self.session))

    @property
    def session(self):
        # type: () -> qi.Session
        """
        Pepper/Nao Robot Session

        Returns
        -------
        session: qi.Session
        """
        return self._session

    @staticmethod
    def create_session(url):
        # type: (str) -> qi.Session
        """
        Create Qi Session with Pepper/Nao Robot

        Parameters
        ----------
        url: str

        Returns
        -------
        session: qi.Session
        """
        application = qi.Application([NAOqiBackend.__name__, "--qi-url={}".format(url)])
        try: application.start()
        except RuntimeError as e:
            raise RuntimeError("Couldn't connect to robot @ {}\n\tOriginal Error: {}".format(url, e))
        return application.session
