from pepper.framework.infra.event.api import Event, EventBus
from pepper.framework.infra.multiprocessing import TopicWorker, RejectionStrategy
from pepper.framework.infra.resource.api import ResourceManager
from pepper.framework.sensor.api import VAD
from pepper.framework.sensor.asr import AbstractASR


class SpeechRecognitionASRWorker(TopicWorker):
    def __init__(self, asr, name, event_bus, resource_manager):
        # type: (AbstractASR, str, EventBus, ResourceManager) -> None
        super(SpeechRecognitionASRWorker, self).__init__(VAD.TOPIC, event_bus, interval=0, name=name,
                                                         resource_manager=resource_manager,
                                                         requires=[VAD.TOPIC], provides=[AbstractASR.TOPIC],
                                                         buffer_size=1024, rejection_strategy=RejectionStrategy.DROP)
        self._asr = asr

    def process(self, event):
        # type: (Event) -> None
        """Speech Transcription Worker"""

        # Every time a voice has been registered by the Voice Activity Detection (long running generator)
        # Transcribe this Voice and obtain a number of UtteranceHypotheses
        voice = event.payload

        hypotheses = self._asr.transcribe(voice.audio_stream)

        if hypotheses:
            # Get Voice Audio Corresponding with Hypotheses
            payload = {'hypotheses': hypotheses, 'audio': voice.audio}
            self.event_bus.publish(AbstractASR.TOPIC, Event(payload, None))