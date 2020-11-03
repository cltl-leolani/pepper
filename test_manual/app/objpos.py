from pepper.app_container import ApplicationContainer, Application
from pepper.framework.application.context import ContextComponent
from pepper.framework.application.display import DisplayComponent
from pepper.framework.application.exploration import ExplorationComponent
from pepper.framework.application.face_detection import FaceRecognitionComponent
from pepper.framework.application.intention import AbstractIntention
from pepper.framework.application.object_detection import ObjectDetectionComponent
from pepper.framework.application.speech_recognition import SpeechRecognitionComponent
from pepper.framework.application.text_to_speech import TextToSpeechComponent


class ObjPosIntention(ApplicationContainer,
                      AbstractIntention,
                      ObjectDetectionComponent, SpeechRecognitionComponent,
                      FaceRecognitionComponent, TextToSpeechComponent,
                      DisplayComponent, ExplorationComponent, ContextComponent):

    def __init__(self):
        super(ObjPosIntention, self).__init__()


if __name__ == '__main__':
    Application(ObjPosIntention()).run()
