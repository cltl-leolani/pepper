from pepper.framework.backend.abstract.microphone import TOPIC as MIC_TOPIC
from pepper.framework.event.api import Event, EventBus
from pepper.framework.multiprocessing import TopicWorker, RejectionStrategy
from pepper.framework.resource.api import ResourceManager
from pepper.framework.sensor.api import VAD


class SpeechRecognitionVADWorker(TopicWorker):
    def __init__(self, vad, name, event_bus, resource_manager):
        # type: (VAD, str, EventBus, ResourceManager) -> None
        super(SpeechRecognitionVADWorker, self).__init__(MIC_TOPIC, event_bus, interval=0, name=name,
                                                         resource_manager=resource_manager,
                                                         requires=[MIC_TOPIC], provides=[VAD.TOPIC],
                                                         buffer_size=1024, rejection_strategy=RejectionStrategy.DROP)
        self._vad = vad

    def process(self, event):
        # type: (Event) -> None
        """Speech Transcription Worker"""

        frames = event.payload
        self._vad.on_audio(frames, self._publish)

    def _publish(self, voice):
        self.event_bus.publish(VAD.TOPIC, Event(voice, None))