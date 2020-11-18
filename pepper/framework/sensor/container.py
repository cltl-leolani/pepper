import logging
import threading
from Queue import Queue
from typing import Iterable

from pepper.framework.backend.container import BackendContainer
from pepper.framework.infra.config.api import ConfigurationContainer
from pepper.framework.infra.di_container import singleton, singleton_for_kw
from pepper.framework.infra.event.api import EventBusContainer
from pepper.framework.infra.resource.api import ResourceContainer
from .api import SensorContainer, SensorWorkerContainer
from .asr import StreamedGoogleASR, GoogleTranslator
from .face_detect import OpenFace
from .obj import ObjectDetectionClient
from .vad import WebRtcVAD
from .worker.face_detection import FaceDetectionWorker
from .worker.object_detection import ObjectDetectionWorker
from .worker.speech_recognition_asr import SpeechRecognitionASRWorker
from .worker.speech_recognition_vad import SpeechRecognitionVADWorker
from .worker.subtitles import SubtitlesWorker
from ..context.api import ContextContainer

logger = logging.getLogger(__name__)


class DefaultSensorWorkerContainer(ContextContainer, SensorWorkerContainer, SensorContainer,
                                   EventBusContainer, ResourceContainer, ConfigurationContainer):

    __workers = Queue()

    def start_object_detector(self, target):
        # type: (str) -> Iterable[threading.Event]
        worker = ObjectDetectionWorker(self.object_detector(target), "ObjectDetectorWorker [{}]".format(target),
                                       self.event_bus, self.resource_manager, self.config_manager)
        DefaultSensorWorkerContainer.__workers.put(worker)

        return (worker.start(),)

    def start_face_detector(self):
        # type: () -> Iterable[threading.Event]
        worker = FaceDetectionWorker(self.face_detector, "FaceDetectorWorker",
                                     self.event_bus, self.resource_manager, self.config_manager)
        DefaultSensorWorkerContainer.__workers.put(worker)

        return (worker.start(),)

    def start_speech_recognition(self):
        # type: () -> Iterable[threading.Event]
        vad_worker = SpeechRecognitionVADWorker(self.vad, "VADWorker", self.event_bus, self.resource_manager)
        asr_worker = SpeechRecognitionASRWorker(self.asr(), "ASRWorker", self.event_bus, self.resource_manager)
        DefaultSensorWorkerContainer.__workers.put(vad_worker)
        DefaultSensorWorkerContainer.__workers.put(asr_worker)

        return (vad_worker.start(), asr_worker.start())

    def start_subtitles(self):
        # type: () -> Iterable[threading.Event]
        worker = SubtitlesWorker(self.context, "SubtitlesWorker", self.event_bus, self.resource_manager, self.config_manager)
        DefaultSensorWorkerContainer.__workers.put(worker)

        return (worker.start(),)

    def stop(self):
        logger.debug("Stopping workers")

        for worker in self.__workers.queue:
            try:
                worker.stop()
            except:
                logger.exception("Failed to stop worker " + worker.name)

        super(DefaultSensorWorkerContainer, self).stop()

        for worker in self.__workers.queue:
            worker.await_stop()
        self.__workers.queue.clear()

        logger.debug("Stopped workers")


class DefaultSensorContainer(BackendContainer, SensorContainer, EventBusContainer, ResourceContainer, ConfigurationContainer):
    logger.info("Initialized DefaultSensorContainer")

    @singleton_for_kw(["language"])
    def asr(self, language=None):
        return StreamedGoogleASR(self.config_manager) if language is None else StreamedGoogleASR(self.config_manager, language)

    @property
    @singleton
    def vad(self):
        return WebRtcVAD(self.resource_manager, self.config_manager)

    @singleton_for_kw(["source_language", "target_language"])
    def translator(self, source_language=None, target_language=None):
        return GoogleTranslator(source_language, target_language)

    @property
    @singleton
    def face_detector(self):
        return OpenFace()

    def object_detector(self, target):
        return ObjectDetectionClient(target)

