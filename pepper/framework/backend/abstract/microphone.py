import logging
from Queue import Queue
from collections import deque
from time import time, sleep

import numpy as np

from pepper.framework.infra.event.api import Event, EventBus
from pepper.framework.infra.resource.api import ResourceManager
from pepper.framework.infra.util import Scheduler

logger = logging.getLogger(__name__)


TOPIC = "pepper.framework.backend.abstract.microphone.topic"
AUDIO_RESOURCE_NAME = "pepper.framework.backend.abstract.audio"
"""Resource name to be shared with the speaker to mute the microphone when the speaker is active.
The AbstractMicrophone holds a reader-lock on this resource.
"""
MIC_RESOURCE_NAME = "pepper.framework.backend.abstract.microphone"
"""Resource name to be shared with application components that allows to retract microphone access from those components.
The AbstractMicrophone holds a writer-lock on this resource.
"""


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
        self._log = logger.getChild(self.__class__.__name__)

        self._rate = rate
        self._channels = channels
        self._event_bus = event_bus
        self._resource_manager = resource_manager
        self._timeout_interval = 1.0 / self._rate

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

        self._muted = True
        self._audio_lock = None
        self._mic_lock = None

    def start(self):
        """Start Microphone Stream"""
        self._resource_manager.provide_resource(AUDIO_RESOURCE_NAME)
        self._resource_manager.provide_resource(MIC_RESOURCE_NAME)
        self._resource_manager.provide_resource(TOPIC)
        self._audio_lock = self._resource_manager.get_read_lock(AUDIO_RESOURCE_NAME)
        self._mic_lock = self._resource_manager.get_write_lock(MIC_RESOURCE_NAME)

        self._processor_scheduler = Scheduler(self._processor, 0, name="MicrophoneThread")
        self._processor_scheduler.start()

    def stop(self):
        """Stop Microphone Stream"""
        if self._audio_lock.locked:
            self._audio_lock.release()
        if self._mic_lock.locked:
            self._mic_lock.release()

        self._processor_scheduler.stop()
        self._resource_manager.retract_resource(TOPIC)
        self._resource_manager.retract_resource(AUDIO_RESOURCE_NAME)
        self._resource_manager.retract_resource(MIC_RESOURCE_NAME)

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

        To avoid interference with text to speech we use the following strategy:

        * Mute the microphone whenever speakers are active
        * Delay speakers until listening stops

        For this we define two resources: AUDIO and MIC
        * Mic and speaker share a Reader-Writer Lock for AUDIO
        * Listeners and mic share a Reader-Writer lock MIC

        and use the following locking strategy:

        * Speaker acquires the AUDIO Writer-lock, signaling interrupt to the AUDIO Reader-lock of the mic
        * Mic acquires the AUDIO Reader-lock, checking for interruption when speakers are not active,
            * if interrupted, mic tries to obtain the MIC write lock (wait for listening to end)
            * when MIC Writer-lock is obtained the mic releases the AUDIO Reader-lock and acquires it again
              (speaker is active, mic is waiting to listen again)
            * when the AUDIO Reader-lock is acquired, it releases the MIC Writer-lock
              (speaker ends, listening starts again)
        """

        if self._queue.empty():
            sleep(self._timeout_interval/10)
            return

        if self._muted:
            self._try_unmute()
        elif self._audio_lock.interrupted:
            self._try_mute()

        # Don't wait forever for the queue, otherwise we can't terminate the worker
        audio = self._queue.get(timeout=2*self._timeout_interval)
        if not self._muted:
            self._event_bus.publish(TOPIC, Event(audio, None))

        # Update Statistics
        self._update_dt(len(audio))

    def _try_unmute(self):
        logger.debug("Try to unmute microphone")
        if self._audio_lock.acquire(blocking=True, timeout=self._timeout_interval):
            self._audio_lock.interrupt_writers(False)
            self._muted = False
            if self._mic_lock.locked:
                self._mic_lock.release()
            logger.info("Microphone unmuted")
        else:
            self._audio_lock.interrupt_writers()

    def _try_mute(self):
        logger.debug("Try to mute microphone")
        if self._mic_lock.acquire(blocking=True, timeout=self._timeout_interval):
            self._mic_lock.interrupt_readers(False)
            self._muted = True
            self._audio_lock.release()
            logger.info("Microphone muted")
        else:
            self._mic_lock.interrupt_readers()

    def _update_dt(self, n_bytes):
        t1 = time()
        self._dt_buffer.append((t1 - self._t0))
        self._t0 = t1
        self._true_rate = n_bytes / np.mean(self._dt_buffer)
