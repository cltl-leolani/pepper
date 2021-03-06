from threading import Thread

import numpy as np
from typing import *

from pepper.framework.application.component import AbstractComponent
from pepper.framework.sensor.api import UtteranceHypothesis
from pepper.framework.sensor.asr import AbstractASR


class SpeechRecognitionComponent(AbstractComponent):
    """
    Speech Recognition Component. Exposes on_transcript Event to Applications.
    """
    def __init__(self):
        # type: () -> None
        super(SpeechRecognitionComponent, self).__init__()

    def start(self):
        self.event_bus.subscribe(AbstractASR.TOPIC, self._on_transcript_handler)
        started_events = self.start_speech_recognition()

        super(SpeechRecognitionComponent, self).start()

        timeout = self.config_manager.get_config("DEFAULT").get_float("dependency_timeout")
        for event in started_events:
            event.wait(timeout=timeout)

        self._log.debug("Initializing SpeechRecognitionComponent")

    def stop(self):
        try:
            self.event_bus.unsubscribe(AbstractASR.TOPIC, self._on_transcript_handler)
        finally:
            super(SpeechRecognitionComponent, self).stop()

        self._log.debug("Initializing SpeechRecognitionComponent")

    def _on_transcript_handler(self, event):
        payload = event.payload
        hypotheses = payload['hypotheses']
        audio = payload['audio']

        self.on_transcript(hypotheses, audio)

    def on_transcript(self, hypotheses, audio):
        # type: (List[UtteranceHypothesis], np.ndarray) -> NoReturn
        """
        On Transcript Event. Called every time an utterance was understood by Automatic Speech Recognition.

        Parameters
        ----------
        hypotheses: List[UtteranceHypothesis]
            Hypotheses about the corresponding utterance
        audio: numpy.ndarray
            Utterance audio
        """
        pass
