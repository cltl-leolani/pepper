

import threading
from sys import stdout, stderr
from time import time

from pepper.framework.application.component import AbstractComponent
from pepper.framework.infra.util import Scheduler


class StatisticsComponent(AbstractComponent):
    """
    Display Realtime Application Performance Statistics
    """

    def __init__(self):
        # type: () -> None
        super(StatisticsComponent, self).__init__()
        self._log.debug("Initializing StatisticsComponent")

        config = self.config_manager.get_config("pepper.framework.component.statistics")
        cam_rate = config.get_int("camera_frame_rate")
        mic_rate = config.get_int("microphone_sample_rate")
        performance_error_threshold = config.get_float("performance_error_threshold")
        live_speech_timeout = config.get_int("live_speech_timeout")

        self.live_speech = ""
        self.live_speech_time = 0

        vad, asr = self.vad, self.asr()

        def worker():
            # Create Voice Activation Bar
            activation = int(vad.activation * 10)
            activation_print = "|" * activation + "." * (10 - activation)
            voice_print = ("<{:10s}>" if vad._voice else "[{:10s}]").format(activation_print)
            empty_voice_print = "[          ]"

            # TODO
            mic_running = True
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
        self._log.debug("Initializing StatisticsComponent worker")
