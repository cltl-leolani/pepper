from pepper.framework.backend.abstract.camera import AbstractCamera
from pepper.framework.backend.abstract.led import AbstractLed
from pepper.framework.backend.abstract.microphone import AbstractMicrophone
from pepper.framework.backend.abstract.motion import AbstractMotion
from pepper.framework.backend.abstract.tablet import AbstractTablet
from pepper.framework.backend.abstract.text_to_speech import AbstractTextToSpeech


class AbstractBackend(object):
    """
    Abstract Backend on which all Backends are based

    Exposes
    :class:`~pepper.framework.backend.abstract.camera.AbstractCamera`,
    :class:`~pepper.framework.backend.abstract.microphone.AbstractMicrophone`,
    :class:`~pepper.framework.backend.abstract.text_to_speech.AbstractTextToSpeech`,
    :class:`~pepper.framework.backend.abstract.led.AbstractLed` and
    :class:`~pepper.framework.backend.abstract.tablet.AbstractTablet`.

    Parameters
    ----------
    camera: AbstractCamera
        Backend :class:`~pepper.framework.backend.abstract.camera.AbstractCamera`
    microphone: AbstractMicrophone
        Backend :class:`~pepper.framework.backend.abstract.microphone.AbstractMicrophone`
    text_to_speech: AbstractTextToSpeech
        Backend :class:`~pepper.framework.backend.abstract.text_to_speech.AbstractTextToSpeech`
    led: AbstractLed
        Backend :class:`~pepper.framework.backend.abstract.led.AbstractLed`
    tablet: AbstractTablet
        Backend :class:`~pepper.framework.backend.abstract.tablet.AbstractTablet`
    """

    def __init__(self, camera, microphone, text_to_speech, motion, led, tablet):
        # type: (AbstractCamera, AbstractMicrophone, AbstractTextToSpeech, AbstractMotion, AbstractLed, AbstractTablet) -> None
        self._camera = camera
        self._microphone = microphone
        self._text_to_speech = text_to_speech
        self._motion = motion
        self._led = led
        self._tablet = tablet

    def start(self):
        if self._camera:
            self._camera.start()
        if self._microphone:
            self._microphone.start()

    def stop(self):
        if self._camera:
            self._camera.stop()
        if self._microphone:
            self._microphone.stop()

    @property
    def camera(self):
        # type: () -> AbstractCamera
        """
        Reference to :class:`~pepper.framework.backdend.abstract.camera.AbstractCamera`

        Returns
        -------
        camera: AbstractCamera
        """
        return self._camera

    @property
    def microphone(self):
        # type: () -> AbstractMicrophone
        """
        Reference to :class:`~pepper.framework.backend.abstract.microphone.AbstractMicrophone`

        Returns
        -------
        microphone: AbstractMicrophone
        """
        return self._microphone

    @property
    def text_to_speech(self):
        # type: () -> AbstractTextToSpeech
        """
        Reference to :class:`~pepper.framework.backend.abstract.text_to_speech.AbstractTextToSpeech`

        Returns
        -------
        text_to_speech: AbstractTextToSpeech
        """
        return self._text_to_speech

    @property
    def motion(self):
        # type: () -> AbstractMotion
        """
        Reference to :class:`~pepper.framework.backend.abstract.motion.AbstractMotion`

        Returns
        -------
        motion: AbstractMotion
        """
        return self._motion

    @property
    def led(self):
        # type: () -> AbstractLed
        """
        Reference to :class:`~pepper.framework.backend.abstract.led.AbstractLed`

        Returns
        -------
        text_to_speech: AbstractLed
        """
        return self._led

    @property
    def tablet(self):
        # type: () -> AbstractTablet
        """
        Reference to :class:`~pepper.framework.backend.abstract.tablet.AbstractTablet`

        Returns
        -------
        tablet: AbstractTablet
        """
        return self._tablet
