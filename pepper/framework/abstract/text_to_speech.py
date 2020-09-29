from typing import Optional, Union

from pepper.framework.abstract.component import AbstractComponent
from pepper.framework.event.api import Event
from pepper.framework.backend.abstract.text_to_speech import TOPIC as TTS_TOPIC


class TextToSpeechComponent(AbstractComponent):
    """
    Text To Speech Component. Exposes the say() Method to Applications
    """

    def __init__(self):
        # type: () -> None
        super(TextToSpeechComponent, self).__init__()

        self._log.info("Initializing TextToSpeechComponent")

    def say(self, text, animation=None, block=False):
        # type: (Union[str, unicode], Optional[str], bool) -> None
        """
        Say Text (with optional Animation) through Text-to-Speech

        Parameters
        ----------
        text: str
            Text to say through Text-to-Speech
        animation: str or None
            (Naoqi) Animation to play
        block: bool
            Whether this function should block or immediately return after calling
        """
        event = Event({'text': text, 'animation': animation, 'block': block}, None)
        self.event_bus.publish(TTS_TOPIC, event)
