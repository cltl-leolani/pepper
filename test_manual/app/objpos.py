from pepper.app_container import ApplicationContainer
from pepper.framework.application.application import AbstractApplication
from pepper.framework.application.face_detection import FaceRecognitionComponent
from pepper.framework.application.object_detection import ObjectDetectionComponent
from pepper.framework.application.text_to_speech import TextToSpeechComponent
from pepper.framework.application.speech_recognition import SpeechRecognitionComponent
from pepper.framework.monitoring import DisplayComponent, SceneComponent, ExploreComponent, ContextComponent


class ObjPosApp(ApplicationContainer,
                AbstractApplication,
                DisplayComponent, SceneComponent,
                ExploreComponent, ContextComponent,
                ObjectDetectionComponent, SpeechRecognitionComponent, FaceRecognitionComponent, TextToSpeechComponent):

    def __init__(self, backend):
        super(ObjPosApp, self).__init__(backend)


if __name__ == '__main__':
    ObjPosApp().run()
