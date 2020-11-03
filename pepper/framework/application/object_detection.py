from typing import List

from pepper import ObjectDetectionTarget
from pepper.framework.application._util import event_payload_handler
from pepper.framework.application.component import AbstractComponent
from pepper.framework.sensor.api import ObjectDetector
from pepper.framework.sensor.obj import Object


class ObjectDetectionComponent(AbstractComponent):
    """
    Perform Object Detection using `Pepper Tensorflow <https://github.com/cltl/pepper_tensorflow>`_
    """
    def __init__(self):
        # type: () -> None
        super(ObjectDetectionComponent, self).__init__()

        config = self.config_manager.get_config("pepper.framework.component.object")
        self._targets = config.get_enum("targets", ObjectDetectionTarget, multi=True)

        self._log.info("Initializing ObjectDetectionComponent")

    def start(self):
        self.event_bus.subscribe(ObjectDetector.TOPIC, self._on_object_handler)
        started_events = []
        for target in self._targets:
            started_events.extend(self.start_object_detector(target))

        super(ObjectDetectionComponent, self).start()

        timeout = self.config_manager.get_config("DEFAULT").get_float("dependency_timeout")
        for event in started_events:
            event.wait(timeout=timeout)

    def stop(self):
        try:
            self.event_bus.unsubscribe(ObjectDetector.TOPIC, self._on_object_handler)
        finally:
            super(ObjectDetectionComponent, self).stop()

    @event_payload_handler
    def _on_object_handler(self, objects):
        self.on_object(objects)

    def on_object(self, objects):
        # type: (List[Object]) -> None
        """
        On Object Event. Called per ObjectDetectionTarget every time one or more objects are detected in a camera frame.

        Parameters
        ----------
        objects: list of Object
            List of Object instances
        """
        pass
