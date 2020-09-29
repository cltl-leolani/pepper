from __future__ import unicode_literals

import re
import urllib
from threading import Timer

from typing import Optional

from pepper.framework.abstract.component import AbstractComponent
from pepper.framework.component import ContextComponent, SpeechRecognitionComponent
from pepper.framework.abstract.text_to_speech import TextToSpeechComponent


class SubtitlesComponent(AbstractComponent):

    def __init__(self):
        # type: () -> None
        super(SubtitlesComponent, self).__init__()

        self._log.info("Initializing SubtitlesComponent")

        config = self.config_manager.get_config("pepper.framework.component.subtitles")
        self._name = config.get("name")
        self._url = config.get("url")
        self._timeout = config.get_float("timeout")

        self._subtitles_timeout_timer = None  # type: Optional[Timer]

        self.require(SubtitlesComponent, TextToSpeechComponent)
        self.require(SubtitlesComponent, SpeechRecognitionComponent)

    def say(self, text, animation=None, block=False):
        # type: (str, str, bool) -> None
        self._show_subtitles('{}:/"{}"'.format(self._name, text))
        super(SubtitlesComponent, self).say(text, animation, block)

    def on_transcript(self, hypotheses, audio):
        speaker = "Human"

        try:
            if isinstance(self, ContextComponent) and self.context.chatting:
                speaker = self.context.chat.speaker
        except AttributeError as e:
            pass

        self._show_subtitles('{}:/"{}"'.format(speaker, hypotheses[0].transcript))
        super(SubtitlesComponent, self).on_transcript(hypotheses, audio)

    def _show_subtitles(self, text):
        # Stop Timeout Timer if running
        if self._subtitles_timeout_timer: self._subtitles_timeout_timer.cancel()

        # Show Subtitles
        text_websafe = urllib.quote(''.join([i for i in re.sub(r'\\\\\S+\\\\', "", text) if ord(i) < 128]))
        self.backend.tablet.show(self._url.format(text_websafe))

        # Start Timeout Timer
        self._subtitles_timeout_timer = Timer(self._timeout, self.backend.tablet.hide)
        self._subtitles_timeout_timer.start()
