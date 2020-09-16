from Queue import Queue

import numpy as np
import webrtcvad
from typing import Iterable

from pepper.framework.abstract import AbstractMicrophone
from pepper.framework.abstract.microphone import TOPIC as MIC_TOPIC
from pepper.framework.config.api import ConfigurationManager
from pepper.framework.event.api import EventBus, Event
from pepper.framework.resource.api import ResourceManager
from .api import VAD, Voice


class WebRtcVAD(VAD):
    """
    Perform Voice Activity Detection on Microphone Input

    Parameters
    ----------
    microphone: AbstractMicrophone
    """
    AUDIO_TYPE = np.int16
    AUDIO_TYPE_BYTES = 2

    MODE = 3

    def __init__(self, microphone, event_bus, resource_manager, configuration_manager):
        # type: (AbstractMicrophone, EventBus, ResourceManager, ConfigurationManager) -> None
        config = configuration_manager("pepper.framework.sensors.vad.webrtc")
        self._mic_rate = config.get_int("microphone_sample_rate")
        self._threshold = config.get_float("threshold")
        self._buffer_size = config.get_int("buffer_size")
        self._voice_window = config.get_int("voice_window")
        audio_frame_ms = config.get_int("audio_frame_ms")

        self._resource_manager = resource_manager
        self._microphone = microphone
        self._mic_lock = None
        self._vad = webrtcvad.Vad(WebRtcVAD.MODE)

        # Voice Activity Detection Frame Size: VAD works in units of 'frames'
        frame_size = audio_frame_ms * self._mic_rate // 1000
        self._frame_size_bytes = frame_size * WebRtcVAD.AUDIO_TYPE_BYTES

        # Audio & Voice Ring-Buffers
        self._audio_buffer = np.zeros((self._buffer_size, frame_size), WebRtcVAD.AUDIO_TYPE)
        self._voice_buffer = np.zeros(self._buffer_size, np.bool)
        self._buffer_index = 0

        self._voice = None
        self._voice_queue = Queue()

        self._frame_buffer = bytearray()

        self._activation = 0

        # Subscribe VAD to Microphone on_audio event
        event_bus.subscribe(MIC_TOPIC, self._on_audio)

    @property
    def activation(self):
        # type: () -> float
        """
        VAD Activation

        Returns
        -------
        activation: float
        """
        return self._activation

    # TODO change the API to accept audio and return voices, i.e.
    # move _on_audio to the place that calls this (iterates this VAD)
    # Then we can simply Mock this class in itests
    @property
    def voices(self):
        # type: () -> Iterable[Voice]
        """
        Get Voices from Microphone Stream

        Yields
        -------
        voices: Iterable[Voice]
        """
        while True:
            yield self._voice_queue.get()

    def _on_audio(self, event):
        # type: (Event) -> None
        """
        (Microphone Callback) Add Audio to VAD

        Parameters
        ----------
        event: Event
        """
        if not self._mic_lock:
            # As there are audio events, the mic lock should be available
            self._mic_lock = self._resource_manager.get_read_lock(MIC_TOPIC)

        # Work through Microphone Stream Frame by Frame
        audio = event.payload
        self._frame_buffer.extend(audio.tobytes())
        while len(self._frame_buffer) >= self._frame_size_bytes:
            self._on_frame(np.frombuffer(self._frame_buffer[:self._frame_size_bytes], WebRtcVAD.AUDIO_TYPE))
            del self._frame_buffer[:self._frame_size_bytes]

    def _on_frame(self, frame):
        # type: (np.ndarray) -> None
        """
        Is-Speech/Is-Not-Speech Logic, called every frame

        Parameters
        ----------
        frame: np.ndarray
        """
        self._activation = self._calculate_activation(frame)

        if not self._mic_lock.locked and not self._mic_lock.acquire(blocking=False):
            # Don't listen if the lock cannot be obtained
            return

        if not self._voice:
            # Only release the lock if there is no voice activity
            if self._mic_lock.interrupted:
                self._mic_lock.release()
                return

            if self._activation > self._threshold:
                # Create New Utterance Object
                self._voice = Voice()

                # Add Buffer Contents to Utterance
                self._voice.add_frame(self._audio_buffer[self._buffer_index:].ravel())
                self._voice.add_frame(self._audio_buffer[:self._buffer_index].ravel())

                # Add Utterance to Utterance Queue
                self._voice_queue.put(self._voice)
        else:
            # If Utterance Ongoing: Add Frame to Utterance Object
            if self.activation > self._threshold:
                self._voice.add_frame(frame)

            # Else: Terminate Utterance
            else:
                self._voice.add_frame(None)
                self._voice = None

    def _calculate_activation(self, frame):
        # type: (np.ndarray) -> float
        """
        Calculate Voice Activation

        Parameters
        ----------
        frame: np.ndarray

        Returns
        -------
        activation: float
        """
        # Update Buffers
        self._audio_buffer[self._buffer_index] = frame
        self._voice_buffer[self._buffer_index] = self._is_speech(frame)
        self._buffer_index = (self._buffer_index + 1) % self._buffer_size

        # Calculate Activation
        voice_window = np.arange(self._buffer_index - self._voice_window, self._buffer_index) % self._buffer_size
        return float(np.mean(self._voice_buffer[voice_window]))

    def _is_speech(self, frame):
        return self._vad.is_speech(frame.tobytes(), self._mic_rate, len(frame))
