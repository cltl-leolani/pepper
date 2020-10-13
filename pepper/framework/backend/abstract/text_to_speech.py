import logging
from Queue import Queue, Empty
from time import sleep

from typing import Optional, Union

from pepper.framework.backend.abstract.microphone import AUDIO_RESOURCE_NAME as AUDIO_RESOURCE
from pepper.framework.infra.event.api import EventBus, Event
from pepper.framework.infra.resource.api import ResourceManager
from pepper.framework.infra.util import Scheduler

logger = logging.getLogger(__name__)


TOPIC = "pepper.framework.backend.abstract.text_to_speech.topic"


class AbstractTextToSpeech(object):
    """
    Abstract Text To Speech

    Parameters
    ----------
    language: str
        `Language Code <https://cloud.google.com/speech/docs/languages>`_
    """

    def __init__(self, language, event_bus, resource_manager):
        # type: (str, EventBus, ResourceManager) -> None
        self._log = logger.getChild(self.__class__.__name__)

        self._language = language
        self._event_bus = event_bus
        self._resource_manager = resource_manager

        self._queue = Queue()
        self._talking_jobs = 0

    def start(self):
        self._scheduler = Scheduler(self._worker, name="TextToSpeechThread")
        self._scheduler.start()

        self._event_bus.subscribe(TOPIC, self._say)
        self._resource_manager.provide_resource(TOPIC)

    def stop(self):
        self._event_bus.unsubscribe(TOPIC, self._say)
        self._resource_manager.retract_resource(TOPIC)

        self._scheduler.stop()

    @property
    def language(self):
        # type: () -> str
        """
        `Language Code <https://cloud.google.com/speech/docs/languages>`_

        Returns
        -------
        language: str
            `Language Code <https://cloud.google.com/speech/docs/languages>`_
        """
        return self._language

    @property
    def talking(self):
        # type: () -> bool
        """
        Returns whether system is currently producing speech

        Returns
        -------
        talking: bool
            Whether system is currently producing speech
        """
        return self._talking_jobs >= 1

    def _say(self, event):
        # type: (Event) -> None
        """
        Say Text (with optional Animation) through Text-to-Speech

        Parameters
        ----------
        event: Event
            Event containing what to say through Text-to-Speech
        """
        payload = event.payload
        text = payload['text']
        animation = payload['animation']
        block = payload['block']

        self._talking_jobs += 1
        self._queue.put((text, animation))

        while block and self.talking and self._scheduler.running:
            sleep(1E-2)

    def on_text_to_speech(self, text, animation=None):
        # type: (Union[str, unicode], Optional[str]) -> None
        """
        Say something through Text to Speech (Implementation)

        Text To Speech Backends should implement this function
        This function should block while speech is being produced

        Parameters
        ----------
        text: str
        animation: str
        """
        raise NotImplementedError()

    def _worker(self):
        if self._queue.empty():
            return

        try:
            with self._resource_manager.get_write_lock(AUDIO_RESOURCE):
                try:
                    self.on_text_to_speech(*self._queue.get(block=False))
                    self._talking_jobs -= 1
                except Empty:
                    # _worker is scheduled anyways, just let the next scheduled worker handle check again
                    pass
        except:
            logger.exception("Failed to convert text to speech")
