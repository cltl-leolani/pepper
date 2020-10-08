from typing import List

from pepper.framework.abstract._util import event_payload_handler
from pepper.framework.abstract.component import AbstractComponent
from pepper.framework.sensor.api import FaceDetector
from pepper.framework.sensor.face import Face


class FaceRecognitionComponent(AbstractComponent):
    """
    Perform Face Detection using :class:`~pepper.sensor.face.OpenFace` and :class:`~pepper.sensor.face.FaceClassifier`
    on every :class:`~pepper.framework.backend.abstract.camera.AbstractCamera` on_image event.
    """
    def __init__(self):
        # type: () -> None
        super(FaceRecognitionComponent, self).__init__()

        self._log.info("Initializing ObjectDetectionComponent")

    def start(self):
        self.event_bus.subscribe(FaceDetector.TOPIC, self._on_face_handler)
        self.event_bus.subscribe(FaceDetector.TOPIC_NEW, self._on_face_new_handler)
        self.event_bus.subscribe(FaceDetector.TOPIC_KNOWN, self._on_face_known_handler)
        self.start_face_detector()

        super(FaceRecognitionComponent, self).start()

    def stop(self):
        try:
            self.event_bus.unsubscribe(FaceDetector.TOPIC, self._on_face_handler)
            self.event_bus.unsubscribe(FaceDetector.TOPIC_NEW, self._on_face_new_handler)
            self.event_bus.unsubscribe(FaceDetector.TOPIC_KNOWN, self._on_face_known_handler)
        finally:
            super(FaceRecognitionComponent, self).stop()

    @event_payload_handler
    def _on_face_handler(self, faces):
        self.on_face(faces)

    @event_payload_handler
    def _on_face_known_handler(self, faces):
        self.on_face_known(faces)

    @event_payload_handler
    def _on_face_new_handler(self, faces):
        self.on_face_new(faces)

    def on_face(self, faces):
        # type: (List[Face]) -> None
        """
        On Face Event. Called with all faces in Image

        Parameters
        ----------
        faces: List[Face]
            List of all faces in Image
        """
        pass

    def on_face_known(self, faces):
        # type: (List[Face]) -> None
        """
        On Face Known Event. Called with all known faces in Image

        Parameters
        ----------
        faces: List[Face]
            List of all Known Faces in Image
        """
        pass

    def on_face_new(self, faces):
        # type: (List[Face]) -> None
        """
        On Face New Event. Called with all new faces in Image

        Parameters
        ----------
        faces: List[Face]
            List of all New Faces in Image
        """
        pass
