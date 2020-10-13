from pepper.app_container import ApplicationContainer, Application
from pepper.framework.application.context import ContextComponent
from pepper.framework.application.face_detection import FaceRecognitionComponent
from pepper.framework.application.intention import AbstractIntention
from pepper.framework.application.monitoring import MonitoringComponent
from pepper.framework.application.object_detection import ObjectDetectionComponent
from pepper.framework.application.speech_recognition import SpeechRecognitionComponent
from pepper.framework.application.statistics import StatisticsComponent
from pepper.framework.application.text_to_speech import TextToSpeechComponent
from pepper.knowledge import animations

"""
HOWTO

1. (Re)Start Docker
2. Start Object Detection pepper_tensorflow/pepper_tensorflow/object_detection.py
3. Start This script!

"""


class BroaderMindIntention(ApplicationContainer,
                           AbstractIntention,
                           StatisticsComponent,  # Show Performance Statistics in Terminal
                           MonitoringComponent,  # Display what Robot (or Computer) sees in browser
                           ContextComponent,  # Context (dependency of MonitoringComponent)
                           ObjectDetectionComponent,  # Object Detection (dependency of MonitoringComponent)
                           FaceRecognitionComponent,  # Face Recognition (dependency of MonitoringComponent)
                           SpeechRecognitionComponent,  # Speech Recognition Component (dependency)
                           TextToSpeechComponent):        # Text to Speech (dependency)

    def __init__(self):
        super(BroaderMindIntention, self).__init__()

    def start(self):
        super(BroaderMindIntention, self).start()

        self.context.start_chat("Human")

    def on_chat_turn(self, utterance):

        # TODO: Change animation to preferred animation
        self.say('hello! ... ...', animation=animations.AFFIRMATIVE)


if __name__ == '__main__':
    Application(BroaderMindIntention()).run()
