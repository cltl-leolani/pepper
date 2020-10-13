from pepper.app_container import ApplicationContainer, Application
from pepper.framework.application.face_detection import FaceRecognitionComponent
from pepper.framework.application.intention import AbstractIntention
from pepper.framework.application.monitoring import MonitoringComponent
from pepper.framework.application.object_detection import ObjectDetectionComponent
from pepper.framework.application.speech_recognition import SpeechRecognitionComponent
from pepper.framework.backend.abstract.camera import TOPIC as CAM_TOPIC
from pepper.framework.backend.abstract.microphone import TOPIC as MIC_TOPIC


class VerboseIntention(ApplicationContainer, AbstractIntention,
                       MonitoringComponent,
                       SpeechRecognitionComponent, ObjectDetectionComponent, FaceRecognitionComponent):

    def __init__(self):
        self.event_bus.subscribe(MIC_TOPIC, lambda e: self._on_event("on_audio", e))
        self.event_bus.subscribe(CAM_TOPIC, lambda e: self._on_event("on_image", e))

    def _on_event(self, description, event):
        self.log.info((description + ": {}").format(event.payload))

    def on_object(self, objects):
        self.log.info("on_object: {}".format(objects))

    def on_face_known(self, faces):
        self.log.info("on_face: {}".format(faces))

    def on_face(self, faces):
        self.log.info("on_person: {}".format(faces))

    def on_face_new(self, faces):
        self.log.info("on_new_person: {}".format(faces))

    def on_transcript(self, hypotheses, audio):
        self.log.info("on_transcript: {}".format(hypotheses, audio.shape))


if __name__ == '__main__':
    Application(VerboseIntention()).run()
