from __future__ import unicode_literals

import qi
from typing import Union, Optional

from pepper.framework.abstract.text_to_speech import AbstractTextToSpeech
from pepper.framework.resource.api import ResourceManager


class NAOqiTextToSpeech(AbstractTextToSpeech):
    """
    NAOqi Text to Speech

    Parameters
    ----------
    session: qi.Session
        Qi Application Session
    """

    SERVICE = "ALAnimatedSpeech"

    def __init__(self, session, language, speed, resource_manager):
        # type: (qi.Session, str, int, ResourceManager) -> None
        super(NAOqiTextToSpeech, self).__init__(language, resource_manager)

        # Subscribe to NAOqi Text to Speech Service
        self._speed = speed
        self._service = session.service(NAOqiTextToSpeech.SERVICE)
        self._log.debug("Booted")

    def on_text_to_speech(self, text, animation=None):
        # type: (Union[str, unicode], Optional[str]) -> None
        """
        Say something through Text to Speech

        Parameters
        ----------
        text: str
        animation: str
        """

        text = text.replace('...', r'\\pau=1000\\')

        if animation:
            self._service.say(r"\\rspd={2}\\^startTag({1}){0}^stopTag({1})".format(text, animation, self._speed))
        else:
            self._service.say(r"\\rspd={1}\\{0}".format(text, self._speed))
