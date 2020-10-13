from random import choice

from pepper.app_container import ApplicationContainer, Application
from pepper.framework.application.face_detection import FaceRecognitionComponent
from pepper.framework.application.intention import AbstractIntention
from pepper.framework.application.object_detection import ObjectDetectionComponent
from pepper.framework.application.speech_recognition import SpeechRecognitionComponent
from pepper.framework.application.text_to_speech import TextToSpeechComponent
from pepper.framework.application.context import ContextComponent
from pepper.framework.application.statistics import StatisticsComponent

from pepper.knowledge import sentences
from pepper.responder import *

RESPONDERS = [
    WikipediaResponder(), WolframResponder()
]


class FactCheckingIntention(AbstractIntention, ApplicationContainer,
                      StatisticsComponent, ContextComponent,
                      ObjectDetectionComponent, FaceRecognitionComponent,
                      SpeechRecognitionComponent, TextToSpeechComponent):

    IGNORE_TIMEOUT = 60

    def __init__(self):
        super(FactCheckingIntention, self).__init__()
        self.response_picker = ResponsePicker(self, RESPONDERS)

    def on_chat_enter(self, name):
        self.context.start_chat(name)
        self.say("{}, {}".format(choice(sentences.GREETING), name))

    def on_chat_exit(self):
        self.say("{}, {}".format(choice(sentences.GOODBYE), self.context.chat.speaker))
        self.context.stop_chat()

    def on_chat_turn(self, utterance):
        self.response_picker.respond(utterance)


if __name__ == '__main__':
    Application(FactCheckingIntention()).run()
