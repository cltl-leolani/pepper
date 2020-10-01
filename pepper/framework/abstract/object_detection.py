from typing import List

from pepper import ObjectDetectionTarget
from pepper.framework.abstract.component import AbstractComponent
from pepper.framework.backend.abstract.camera import TOPIC as CAM_TOPIC
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
        for target in self._targets:
            self.start_object_detector(target)

        super(ObjectDetectionComponent, self).start()

    def stop(self):
        self.event_bus.unsubscribe(ObjectDetector.TOPIC, self._on_object_handler)
        super(ObjectDetectionComponent, self).stop()

    def _on_object_handler(self, event):
        self.on_object(event.payload)

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
