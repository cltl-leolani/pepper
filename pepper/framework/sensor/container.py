import logging
from Queue import Queue

from pepper.framework.backend.container import BackendContainer
from pepper.framework.config.api import ConfigurationContainer
from pepper.framework.di_container import singleton, singleton_for_kw
from pepper.framework.event.api import EventBusContainer
from pepper.framework.resource.api import ResourceContainer
from .api import SensorContainer, SensorWorkerContainer
from .asr import StreamedGoogleASR, GoogleTranslator
from .face_detect import OpenFace
from .obj import ObjectDetectionClient
from .vad import WebRtcVAD
from .worker.object_detection import ObjectDetectionWorker

logger = logging.getLogger(__name__)


class DefaultSensorWorkerContainer(SensorWorkerContainer, EventBusContainer, ResourceContainer, ConfigurationContainer):

    __workers = Queue()

    def start_object_detector(self, target):
        worker = ObjectDetectionWorker(self.object_detector(target), "ObjectDetector [{}]".format(target),
                                       self.event_bus, self.resource_manager, self.config_manager)
        DefaultSensorWorkerContainer.__workers.put(worker)
        worker.start()

    @property
    def sensor_workers(self):
        return tuple(DefaultSensorWorkerContainer.__workers.queue)


class DefaultSensorContainer(BackendContainer, SensorContainer, EventBusContainer, ResourceContainer, ConfigurationContainer):
    logger.info("Initialized DefaultSensorContainer")

    @singleton_for_kw(["language"])
    def asr(self, language=None):
        return StreamedGoogleASR(self.config_manager) if language is None else StreamedGoogleASR(self.config_manager, language)

    @property
    @singleton
    def vad(self):
        return WebRtcVAD(self.event_bus, self.resource_manager, self.config_manager)

    @singleton_for_kw(["source_language", "target_language"])
    def translator(self, source_language=None, target_language=None):
        return GoogleTranslator(source_language, target_language)

    @property
    @singleton
    def face_detector(self):
        return OpenFace()

    def object_detector(self, target):
        return ObjectDetectionClient(target)

