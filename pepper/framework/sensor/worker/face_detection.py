from pepper import config
from pepper.framework.backend.abstract.camera import TOPIC as CAM_TOPIC
from pepper.framework.infra.config.api import ConfigurationManager
from pepper.framework.infra.event.api import Event, EventBus
from pepper.framework.infra.multiprocessing import TopicWorker
from pepper.framework.infra.resource.api import ResourceManager
from pepper.framework.sensor.api import FaceDetector
from pepper.framework.sensor.face import FaceClassifier


class FaceDetectionWorker(TopicWorker):
    def __init__(self, face_detector, name, event_bus, resource_manager, config_manager):
        # type: (FaceDetector, str, EventBus, ResourceManager, ConfigurationManager) -> None
        super(FaceDetectionWorker, self).__init__(CAM_TOPIC, event_bus, interval=0, name=name,
                                                  resource_manager=resource_manager, requires=[CAM_TOPIC],
                                                  provides=[FaceDetector.TOPIC, FaceDetector.TOPIC_NEW, FaceDetector.TOPIC_KNOWN])
        configuration = config_manager.get_config("pepper.framework.component.face")
        self._threshold = configuration.get_float("threshold")
        friends_dir = configuration.get("friends_dir")
        new_dir = configuration.get("new_dir")

        # Import Face Data (Friends & New)
        people = FaceClassifier.load_directory(friends_dir)
        people.update(FaceClassifier.load_directory(new_dir))
        self._face_classifier = FaceClassifier(people)

        self._face_detector = face_detector

    def process(self, event):
        # type: (Event) -> None
        """Find and Classify Faces in Images"""

        # Get latest Image from Mailbox
        image = event.payload

        # Get All Face Representations from OpenFace & Initialize Known/New Face Categories
        on_face = [self._face_classifier.classify(r, b, image) for r, b in self._face_detector.represent(image.image)]
        on_face_known = []
        on_face_new = []

        # Distribute Faces over Known & New (Keeping them in the general on_face)
        for face in on_face:
            if face.name == config.HUMAN_UNKNOWN:
                if face.confidence >= 1.0:
                    on_face_new.append(face)
            elif face.confidence > self._threshold:
                on_face_known.append(face)

        if on_face:
            self.event_bus.publish(FaceDetector.TOPIC, Event(on_face, None))
        if on_face_known:
            self.event_bus.publish(FaceDetector.TOPIC_KNOWN, Event(on_face_known, None))
        if on_face_new:
            self.event_bus.publish(FaceDetector.TOPIC_NEW, Event(on_face_new, None))