from pepper.app_container import ApplicationContainer
from pepper.framework.abstract.application import AbstractApplication
from pepper.framework.abstract.face_detection import FaceRecognitionComponent
from pepper.framework.abstract.object_detection import ObjectDetectionComponent
from pepper.framework.abstract.text_to_speech import TextToSpeechComponent
from pepper.framework.abstract.speech_recognition import SpeechRecognitionComponent
from pepper.framework.component import DisplayComponent, SceneComponent, ExploreComponent, ContextComponent


class ObjPosApp(ApplicationContainer,
                AbstractApplication,
                DisplayComponent, SceneComponent,
                ExploreComponent, ContextComponent,
                ObjectDetectionComponent, SpeechRecognitionComponent, FaceRecognitionComponent, TextToSpeechComponent):

    def __init__(self, backend):
        super(ObjPosApp, self).__init__(backend)


if __name__ == '__main__':
    ObjPosApp().run()
