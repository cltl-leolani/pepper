import unittest

import mock
import numpy as np

from pepper.framework.infra.config.api import ConfigurationManager
from pepper.framework.infra.resource.api import ResourceManager, ReadLock
from pepper.framework.sensor.vad import AbstractVAD
from test.util import TestConfiguration

# 2 channels, 10ms, 16000Hz
VAD_FRAME_SIZE = (2 * 10 * 16000) // 1000


class TestVAD(AbstractVAD):
    def __init__(self, resource_manager, config_manager, is_speech=True):
        super(TestVAD, self).__init__(resource_manager, config_manager)
        self.vad_frames = []
        self._test_speech = is_speech

    def _is_speech(self, vad_frame):
        self.vad_frames.append(vad_frame)
        try:
            return self._test_speech(vad_frame)
        except TypeError:
            return self._test_speech


class AbstractVADTestCase(unittest.TestCase):
    def setUp(self, is_speech=True):
        test_config = {
            "microphone_sample_rate": 16000,
            "microphone_channels": 2,
            "threshold": 1.0,
            "buffer_size": 10,
            "voice_window": 5,
            "audio_frame_ms": 10
        }
        mock_config_manager = mock.create_autospec(ConfigurationManager)
        mock_config_manager.get_config.return_value = TestConfiguration(test_config)

        mock_lock = mock.create_autospec(ReadLock)
        mock_lock.acquire.return_value = True
        mock_lock.interrupted = False

        mock_resource_manager = mock.create_autospec(ResourceManager)
        mock_resource_manager.get_read_lock.return_value = mock_lock

        self.vad = TestVAD(mock_resource_manager, mock_config_manager, is_speech)

    def test_single_frame(self):
        frames = np.zeros(VAD_FRAME_SIZE, dtype=np.int16)
        self.vad.on_audio(frames, lambda voice: None)
        self.assertEqual(1, len(self.vad.vad_frames))
        self.assertEqual((VAD_FRAME_SIZE//2, 2), self.vad.vad_frames[0].shape)

    def test_multiple_frames(self):
        frames = np.zeros(10 * VAD_FRAME_SIZE, dtype=np.int16)
        self.vad.on_audio(frames, lambda voice: None)
        self.assertEqual(10, len(self.vad.vad_frames))
        self.assertEqual(((VAD_FRAME_SIZE//2, 2),) * 10, tuple(f.shape for f in self.vad.vad_frames))

    def test_partial_frame(self):
        frames = np.zeros(int(10.5 * VAD_FRAME_SIZE), dtype=np.int16)
        self.vad.on_audio(frames, lambda voice: None)
        self.assertEqual(10, len(self.vad.vad_frames))
        self.assertEqual(((VAD_FRAME_SIZE//2, 2),) * 10, tuple(f.shape for f in self.vad.vad_frames))

        frames = np.zeros(int(10.5 * VAD_FRAME_SIZE), dtype=np.int16)
        self.vad.on_audio(frames, lambda voice: None)
        self.assertEqual(21, len(self.vad.vad_frames))
        self.assertEqual(((VAD_FRAME_SIZE//2, 2),) * 21, tuple(f.shape for f in self.vad.vad_frames))

    def test_single_voice(self):
        def is_speech(frame):
            return frame[0][0]

        self.setUp(is_speech)

        # Base signal
        frames = np.zeros(100 * VAD_FRAME_SIZE, dtype=np.int16)

        # Speech from VAD frame 20-40
        voice_start = 20 * VAD_FRAME_SIZE
        voice_end = 40 * VAD_FRAME_SIZE
        frames[voice_start:voice_end] = 1.0
        self.assertEqual(20 * VAD_FRAME_SIZE, sum(frames))

        voices = []
        self.vad.on_audio(frames, lambda voice: voices.append(voice))

        self.assertEqual(100, len(self.vad.vad_frames))
        self.assertEqual(((VAD_FRAME_SIZE//2, 2),) * 100, tuple(f.shape for f in self.vad.vad_frames))

        self.assertEqual(1, len(voices))
        audio = voices[0].audio
        # buffer_length == 10 and vad_window == 5, thus audio starts 5 VAD frames before actual speech
        self.assertEqual(25 * VAD_FRAME_SIZE, len(audio))
        self.assertTrue(all(x == 0 for x in audio[:5 * VAD_FRAME_SIZE]))
        self.assertTrue(all(x == 1.0 for x in audio[5 * VAD_FRAME_SIZE:]))

    def test_multiple_voices(self):
        def is_speech(frame):
            return frame[0][0]

        self.setUp(is_speech)

        # Base signal
        frames = np.zeros(100 * VAD_FRAME_SIZE, dtype=np.int16)

        # Speech from VAD frame 20-40
        voice_start = 20 * VAD_FRAME_SIZE
        voice_end = 40 * VAD_FRAME_SIZE
        frames[voice_start:voice_end] = 1.0
        self.assertEqual(20 * VAD_FRAME_SIZE, sum(frames))

        # Speech from VAD frame 60-70
        voice_start = 60 * VAD_FRAME_SIZE
        voice_end = 70 * VAD_FRAME_SIZE
        frames[voice_start:voice_end] = 1.0
        self.assertEqual(30 * VAD_FRAME_SIZE, sum(frames))

        voices = []
        self.vad.on_audio(frames, lambda voice: voices.append(voice))

        self.assertEqual(100, len(self.vad.vad_frames))
        self.assertEqual(((VAD_FRAME_SIZE//2, 2),) * 100, tuple(f.shape for f in self.vad.vad_frames))

        self.assertEqual(2, len(voices))
        audio = voices[0].audio
        # buffer_length == 10 and vad_window == 5, thus audio starts 5 VAD frames before actual speech
        self.assertEqual(25 * VAD_FRAME_SIZE, len(audio))
        self.assertTrue(all(x == 0 for x in audio[:5 * VAD_FRAME_SIZE]))
        self.assertTrue(all(x == 1.0 for x in audio[5 * VAD_FRAME_SIZE:]))

        audio = voices[1].audio
        # buffer_length == 10 and vad_window == 5, thus audio starts 5 VAD frames before actual speech
        self.assertEqual(15 * VAD_FRAME_SIZE, len(audio))
        self.assertTrue(all(x == 0 for x in audio[:5 * VAD_FRAME_SIZE]))
        self.assertTrue(all(x == 1.0 for x in audio[5 * VAD_FRAME_SIZE:]))


if __name__ == '__main__':
    unittest.main()
