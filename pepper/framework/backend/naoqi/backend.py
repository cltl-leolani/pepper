from pepper.framework.abstract import AbstractBackend
from pepper.framework.backend.system import SystemCamera, SystemMicrophone, SystemTextToSpeech
from pepper.framework.backend.naoqi import NAOqiCamera, NAOqiMicrophone, NAOqiTextToSpeech
from pepper import config

import qi


class NAOqiBackend(AbstractBackend):
    """
    Initialize NAOqi Backend

    Parameters
    ----------
    url: str
        NAOqi Robot URL
    camera_resolution: CameraResolution
        NAOqi Camera Resolution
    camera_rate: int
        NAOqi Camera Rate
    microphone_index: int
        NAOqi Microphone Index
    language: str
        NAOqi Language
    use_system_camera: bool
        Use System Camera instead of NAOqi Camera
    use_system_microphone: bool
        Use System Microphone instead of NAOqi Microphone
    use_system_text_to_speech: bool
        Use System TextToSpeech instead of NAOqi TextToSpeech

    See Also
    --------
    http://doc.aldebaran.com/2-5/index_dev_guide.html
    """
    def __init__(self, url=config.NAOQI_URL,
                 camera_resolution=config.CAMERA_RESOLUTION, camera_rate=config.CAMERA_FRAME_RATE,
                 microphone_index=config.NAOQI_MICROPHONE_INDEX, language=config.APPLICATION_LANGUAGE,
                 use_system_camera=False, use_system_microphone=False, use_system_text_to_speech=False):

        self._url = url
        self._session = self.create_session(self._url)

        if use_system_camera: camera = SystemCamera(camera_resolution, camera_rate)
        else: camera = NAOqiCamera(self.session, camera_resolution, camera_rate)

        if use_system_microphone: microphone = SystemMicrophone(16000, 1)
        else: microphone = NAOqiMicrophone(self.session, microphone_index)

        if use_system_text_to_speech: text_to_speech = SystemTextToSpeech(language)
        else: text_to_speech = NAOqiTextToSpeech(self.session, language)

        super(NAOqiBackend, self).__init__(camera, microphone, text_to_speech)

    @property
    def url(self):
        """
        Pepper/Nao Robot URL

        Returns
        -------
        url: str
        """
        return self._url

    @property
    def session(self):
        """
        Pepper/Nao Robot Session

        Returns
        -------
        session: qi.Session
        """
        return self._session

    @staticmethod
    def create_session(url):
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