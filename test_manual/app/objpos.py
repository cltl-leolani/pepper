from pepper.app_container import ApplicationContainer
from pepper.framework.application.application import AbstractApplication
from pepper.framework.application.face_detection import FaceRecognitionComponent
from pepper.framework.application.object_detection import ObjectDetectionComponent
from pepper.framework.application.text_to_speech import TextToSpeechComponent
from pepper.framework.application.speech_recognition import SpeechRecognitionComponent


class ObjPosApp(ApplicationContainer,
                AbstractApplication,
                ObjectDetectionComponent, SpeechRecognitionComponent,
                FaceRecognitionComponent, TextToSpeechComponent,
                DisplayComponent, SceneComponent,
                ExploreComponent, ContextComponent,):

    def __init__(self, backend):
        super(ObjPosApp, self).__init__(backend)


if __name__ == '__main__':
    ObjPosApp().run()
