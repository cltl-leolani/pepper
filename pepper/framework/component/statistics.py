from __future__ import print_function

import threading
from sys import stdout, stderr
from time import time

from pepper.framework.abstract.component import AbstractComponent
from pepper.framework.component import SpeechRecognitionComponent
from pepper.framework.abstract.microphone import TOPIC as MIC_TOPIC
from pepper.framework.util import Scheduler


class StatisticsComponent(AbstractComponent):
    """
    Display Realtime Application Performance Statistics
    """

    def __init__(self):
        # type: () -> None
        super(StatisticsComponent, self).__init__()
        self._log.info("Initializing StatisticsComponent")

        config = self.config_manager.get_config("pepper.framework.component.statistics")
        cam_rate = config.get_int("camera_frame_rate")
        mic_rate = config.get_int("microphone_sample_rate")
        performance_error_threshold = config.get_float("performance_error_threshold")
        live_speech_timeout = config.get_int("live_speech_timeout")

        self.live_speech = ""
        self.live_speech_time = 0

        # Require Speech Recognition Component and Get Information from it
        speech_recognition = self.require(StatisticsComponent, SpeechRecognitionComponent)  # type: SpeechRecognitionComponent
        vad, asr = speech_recognition.vad, speech_recognition.asr()
        mic_lock = self.resource_manager.get_read_lock(MIC_TOPIC)

        def worker():
            # Create Voice Activation Bar
            activation = int(vad.activation * 10)
            activation_print = "|" * activation + "." * (10 - activation)
            voice_print = ("<{:10s}>" if vad._voice else "[{:10s}]").format(activation_print)
            empty_voice_print = "[          ]"

            # Get Microphone Related Information
            if mic_lock.interrupted():
                mic_lock.release()
            else:
                mic_running = mic_lock.locked or mic_lock.acquire(blocking=False)
            mic_rate_true = self.backend.microphone.true_rate

            # Get Camera Related Information
            cam_rate_true = self.backend.camera.true_rate

            # If Camera and/or Microphone are not running as fast as expected -> show stderr message instead of stdout
            error = (cam_rate_true < cam_rate * performance_error_threshold or
                     mic_rate_true < float(mic_rate) * performance_error_threshold)

            # Show Speech to Text Transcript 'live' as it happens
            if asr.live:
                self.live_speech = asr.live
                self.live_speech_time = time()
            elif time() - self.live_speech_time > live_speech_timeout:
                self.live_speech = ""

            # Display Statistics
            print("\rThreads {:2d} | Cam {:4.1f} Hz | Mic {:4.1f} kHz | STT {:12s} >>> {}".format(
                threading.active_count(),
                cam_rate_true,
                mic_rate_true / 1000.0,
                voice_print if mic_running else empty_voice_print,
                self.live_speech),
                end="", file=(stderr if error else stdout))

        # Run 10 times a second
        # TODO: Bit Much?
        schedule = Scheduler(worker, 0.1)
        schedule.start()
        self._log.info("Started StatisticsComponent worker")
