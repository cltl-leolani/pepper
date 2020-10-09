from collections import deque

import numpy as np
import webrtcvad
from typing import Iterable

from pepper.framework.backend.abstract.microphone import AbstractMicrophone
from pepper.framework.backend.abstract.microphone import MIC_RESOURCE_NAME as MIC_RESOURCE
from pepper.framework.infra.config.api import ConfigurationManager
from pepper.framework.infra.resource.api import ResourceManager
from .api import VAD, Voice


class AbstractVAD(VAD):
    """
    Perform Voice Activity Detection on Microphone Input

    Parameters
    ----------
    microphone: AbstractMicrophone
    """
    AUDIO_TYPE = np.int16
    AUDIO_TYPE_BYTES = 2

    MODE = 3

    def __init__(self, resource_manager, configuration_manager):
        # type: (ResourceManager, ConfigurationManager) -> None
        config = configuration_manager.get_config("pepper.framework.sensors.vad.webrtc")
        self._mic_rate = config.get_int("microphone_sample_rate")
        self._channels = config.get_int("microphone_channels")
        self._threshold = config.get_float("threshold")
        self._buffer_size = config.get_int("buffer_size")
        self._voice_window = config.get_int("voice_window")

        self._resource_manager = resource_manager
        self._mic_lock = None

        self._input_buffer = self._init_buffer()

        # Voice Activity Detection Frame Size: VAD works with chunks of length audio_frame_ms
        audio_frame_ms = config.get_int("audio_frame_ms")
        self._vad_frame_size = audio_frame_ms * self._mic_rate // 1000

        self._activation_window = deque(maxlen=self._voice_window)
        self._activation = 0

        self._voice = None

    def _init_buffer(self):
        return np.empty((0, self._channels), dtype=np.int16)

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

    def on_audio(self, frames, voice_callback):
        # type: (np.array) -> Iterable[Voice]
        if not len(frames):
            return None

        if not self._mic_lock:
            # As there are audio events, the mic lock should be available
            self._mic_lock = self._resource_manager.get_read_lock(MIC_RESOURCE)

        # Work through Microphone Stream Frame by Frame
        # split flat input into channels
        input_frames = frames.reshape((-1, self._channels))

        self._input_buffer = np.concatenate((self._input_buffer, input_frames))

        vad_frame_cnt = self._input_buffer.shape[0] // self._vad_frame_size
        if vad_frame_cnt == 0:
            return

        vad_size = vad_frame_cnt * self._vad_frame_size
        vad_frames = self._input_buffer[:vad_size].reshape((vad_frame_cnt, -1, self._channels))

        for index, vad_frame in enumerate(vad_frames):
            voice = self._on_vad_frame(vad_frame, index)
            if voice:
                voice_callback(voice)

        # Keep the remainder if there is a partially filled VAD frame
        self._input_buffer = self._input_buffer[vad_size:]

    def _on_vad_frame(self, vad_frame, index):
        # type: (np.ndarray) -> None
        """
        Is-Speech/Is-Not-Speech Logic, called every frame

        Parameters
        ----------
        vad_frame: np.ndarray
        """
        self._activation = self._calculate_activation(vad_frame)

        if not self._mic_lock.locked and not self._mic_lock.acquire(blocking=False):
            # Don't listen if the lock cannot be obtained and
            # don't keep audio from before listening was interrupted
            self._input_buffer = self._init_buffer()
            return

        if not self._voice:
            # Only release the lock if there is no voice activity
            if self._mic_lock.interrupted:
                self._mic_lock.release()
                return

            if self._activation >= self._threshold:
                # Create New Utterance Object
                self._voice = Voice()

                # Add Buffer Contents to Utterance
                start = max(0, (index + 1 - self._buffer_size) * vad_frame.shape[0])
                end = (index + 1) * vad_frame.shape[0]

                x = self._input_buffer[start:end]
                self._voice.add_frame(self._input_buffer[start:end].ravel())

                # Add Utterance to Utterance Queue
                return self._voice
        else:
            # If Utterance Ongoing: Add Frame to Utterance Object
            if self.activation >= self._threshold:
                self._voice.add_frame(vad_frame.ravel())

            # Else: Terminate Utterance
            else:
                self._voice.add_frame(None)
                self._voice = None

        return None

    def _calculate_activation(self, vad_frame):
        # type: (np.ndarray) -> float
        """
        Calculate Voice Activation over the VAD window after adding the frame.

        Parameters
        ----------
        frame: np.ndarray

        Returns
        -------
        activation: float
        """
        self._activation_window.append(float(self._is_speech(vad_frame)))

        return sum(self._activation_window) / len(self._activation_window)

    def _is_speech(self, vad_frame):
        raise NotImplementedError()


class WebRtcVAD(AbstractVAD):
    def __init__(self, resource_manager, configuration_manager):
        super(WebRtcVAD, self).__init__(resource_manager, configuration_manager)

        self._vad = webrtcvad.Vad(WebRtcVAD.MODE)

    def _is_speech(self, vad_frame):
        """
        The WebRTC VAD only accepts 16 - bit mono PCM audio, sampled at 8000,
        16000, 32000 or 48000 Hz.A frame must be either 10, 20, or 30 ms in
        duration.
        """
        mono_frame = vad_frame.sum(axis=1).ravel()

        return self._vad.is_speech(mono_frame.tobytes(), self._mic_rate, len(mono_frame))
