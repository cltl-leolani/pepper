from pepper.framework.backend.abstract.camera import TOPIC as CAM_TOPIC
from pepper.framework.infra.config.api import ConfigurationManager
from pepper.framework.infra.event.api import Event, EventBus
from pepper.framework.infra.multiprocessing import TopicWorker
from pepper.framework.infra.resource.api import ResourceManager
from pepper.framework.sensor.api import ObjectDetector


class ObjectDetectionWorker(TopicWorker):
    def __init__(self, object_detector, name, event_bus, resource_manager, config_manager):
        # type: (ObjectDetector, str, EventBus, ResourceManager, ConfigurationManager) -> None
        super(ObjectDetectionWorker, self).__init__(CAM_TOPIC, event_bus, interval=0, name=name,
                 resource_manager=resource_manager, requires=[CAM_TOPIC], provides=[ObjectDetector.TOPIC])
        config = config_manager.get_config("pepper.framework.component.object")
        self._threshold = config.get_float("threshold")

        self._object_detector = object_detector

    def process(self, event):
        # type: (Event) -> None
        image = event.payload

        objects = [obj for obj in self._object_detector.classify(image) if obj.confidence > self._threshold]

        if objects:
            self.event_bus.publish(ObjectDetector.TOPIC, Event(objects, None))