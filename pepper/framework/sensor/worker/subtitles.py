from __future__ import unicode_literals

import re
import urllib
from threading import Timer

from typing import Optional

from pepper.framework.backend.abstract.text_to_speech import TOPIC as TTS_TOPIC
from pepper.framework.backend.abstract.tablet import TOPIC as TABLET_TOPIC
from pepper.framework.infra.config.api import ConfigurationManager
from pepper.framework.context.api import Context
from pepper.framework.infra.event.api import EventBus, Event
from pepper.framework.infra.multiprocessing import TopicWorker
from pepper.framework.infra.resource.api import ResourceManager
from pepper.framework.sensor.asr import AbstractASR

TOPICS = [AbstractASR.TOPIC, TTS_TOPIC]


class SubtitlesWorker(TopicWorker):
    def __init__(self, context, name, event_bus, resource_manager, config_manager):
        # type: (Context, str, EventBus, ResourceManager, ConfigurationManager) -> None
        super(SubtitlesWorker, self).__init__(TOPICS, event_bus, interval=0, name=name,
              resource_manager=resource_manager, requires=TOPICS, provides=[TABLET_TOPIC])
        config = config_manager.get_config("pepper.framework.component.subtitles")
        self._name = config.get("name")
        self._url = config.get("url")
        self._timeout = config.get_float("timeout")

        self._context = context
        self._subtitles_timeout_timer = None  # type: Optional[Timer]

    def process(self, event):
        # type: (Event) -> None
        if AbstractASR.TOPIC == event.metadata.topic:
            self.on_utterance(event.payload['text'])
        elif TTS_TOPIC == event.metadata.topic:
            self.on_transcript(event.payload['hypotheses'])

    def on_utterance(self, text):
        # type: (str) -> None
        self.show_subtitles('{}:/"{}"'.format(self._name, text))

    def on_transcript(self, hypotheses):
        # type: (str) -> None
        speaker = "Human"

        try:
            if self._context and self._context.chatting:
                speaker = self._context.chat.speaker
        except AttributeError as e:
            pass

        self.show_subtitles('{}:/"{}"'.format(speaker, hypotheses[0].transcript))

    def show_subtitles(self, text):
        # type: (str) -> None
        # Stop Timeout Timer if running
        if self._subtitles_timeout_timer: self._subtitles_timeout_timer.cancel()

        # Show Subtitles
        text_websafe = urllib.quote(''.join([i for i in re.sub(r'\\\\\S+\\\\', "", text) if ord(i) < 128]))
        event = Event({'url': self._url.format(text_websafe)}, None)
        self.event_bus.publish(TABLET_TOPIC, event)

        # Start Timeout Timer
        self._subtitles_timeout_timer = Timer(self._timeout, self.hide_subtitles)
        self._subtitles_timeout_timer.start()

    def hide_subtitles(self):
        # type: () -> None
        event = Event({'url': None}, None)
        self.event_bus.publish(TABLET_TOPIC, event)