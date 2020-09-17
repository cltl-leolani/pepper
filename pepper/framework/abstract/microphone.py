import logging
from Queue import Queue
from collections import deque
from time import time

import numpy as np

from pepper.framework.event.api import Event
from pepper.framework.resource.api import ResourceManager
from pepper.framework.util import Scheduler

logger = logging.getLogger(__name__)


TOPIC = "pepper.framework.abstract.microphone.audio"


class AbstractMicrophone(object):
    def __init__(self, rate, channels, event_bus, resource_manager):
        # type: (int, int, EventBus, ResourceManager) -> None
        """
        Initialize AbstractMicrophone

        Parameters
        ----------
        rate: int
            Samples per Second
        channels: int
            Number of Channels
        event_bus: EventBus
            EventBus to send events when audio is captured
        resource_manager : ResourceManager
            Resource manager to manage access to the microphone resource
        """
        self._rate = rate
        self._channels = channels
        self._event_bus = event_bus
        self._resource_manager = resource_manager

        # Variables to do some performance statistics
        self._dt_buffer = deque([], maxlen=32)
        self._true_rate = rate
        self._t0 = time()

        # Create Queue and Sound Processor:
        #   Each time audio samples are captured it is put in the audio processing queue
        #   In a separate thread, the _processor worker takes these samples and publishes them as events.
        #   This way, samples are not accidentally skipped (NAOqi has some very strict timings)
        self._queue = Queue()
        self._processor_scheduler = None

        self._log = logger.getChild(self.__class__.__name__)

    def start(self):
        """Start Microphone Stream"""
        self._resource_manager.provide_resource(TOPIC)
        self._processor_scheduler = Scheduler(self._processor, 0, name="MicrophoneThread")
        self._processor_scheduler.start()

    def stop(self):
        """Stop Microphone Stream"""
        self._processor_scheduler.stop()
        self._resource_manager.retract_resource(TOPIC)

    @property
    def true_rate(self):
        # type: () -> float
        """
        Actual Audio bit rate

        Audio bit rate after accounting for latency & performance realities

        Returns
        -------
        true_rate:
            Actual Audio bit rate
        """
        return self._true_rate

    # TODO With an async event bus we can directly post events to the event bus
    def on_audio(self, audio):
        # type: (np.ndarray) -> None
        """
        On Audio Event, Called for every frame of audio captured by Microphone

        Microphone implementations should call this function for every frame of audio acquired by Microphone

        Parameters
        ----------
        audio: np.ndarray
        """
        self._queue.put(audio)

    def _processor(self):
        """
        Audio Processor

        Publishes audio events for each audio frame, threaded, for higher audio throughput
        """
        audio = self._queue.get()
        self._event_bus.publish(TOPIC, Event(audio, None))

        # Update Statistics
        self._update_dt(len(audio))

    def _update_dt(self, n_bytes):
        t1 = time()
        self._dt_buffer.append((t1 - self._t0))
        self._t0 = t1
        self._true_rate = n_bytes / np.mean(self._dt_buffer)
