from random import choice

from pepper.app_container import ApplicationContainer
from pepper.framework.abstract.application import AbstractApplication
from pepper.framework.abstract.intention import AbstractIntention
from pepper.framework.abstract.object_detection import ObjectDetectionComponent
from pepper.framework.abstract.face_detection import FaceRecognitionComponent
from pepper.framework.abstract.text_to_speech import TextToSpeechComponent
from pepper.framework.component import StatisticsComponent, ContextComponent, \
    SpeechRecognitionComponent
from pepper.knowledge import sentences
from pepper.responder import *

RESPONDERS = [
    WikipediaResponder(), WolframResponder()
]


class FactCheckingApp(AbstractApplication, ApplicationContainer,
                      StatisticsComponent, ContextComponent,
                      ObjectDetectionComponent, FaceRecognitionComponent,
                      SpeechRecognitionComponent, TextToSpeechComponent):

    def __init__(self, backend):
        super(FactCheckingApp, self).__init__(backend)


class DefaultIntention(AbstractIntention, FactCheckingApp):
    IGNORE_TIMEOUT = 60

    def __init__(self, application):
        super(DefaultIntention, self).__init__(application)
        self.response_picker = ResponsePicker(self, RESPONDERS)

    def on_chat_enter(self, name):
        self.context.start_chat(name)
        self.say("{}, {}".format(choice(sentences.GREETING), name))

    def on_chat_exit(self):
        self.say("{}, {}".format(choice(sentences.GOODBYE), self.context.chat.speaker))
        self.context.stop_chat()

    def on_chat_turn(self, utterance):
        responder = self.response_picker.respond(utterance)


if __name__ == '__main__':

    while True:
        # Initialize Application
        application = FactCheckingApp()

        # Initialize Intention
        DefaultIntention(application)

        # Run Application
        application.run()
