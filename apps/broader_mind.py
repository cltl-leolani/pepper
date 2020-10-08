from pepper.app_container import ApplicationContainer
from pepper.framework.abstract.application import AbstractApplication
from pepper.framework.abstract.object_detection import ObjectDetectionComponent
from pepper.framework.abstract.text_to_speech import TextToSpeechComponent
from pepper.framework.abstract.face_detection import FaceRecognitionComponent
from pepper.framework.abstract.speech_recognition import SpeechRecognitionComponent
from pepper.framework.abstract.context import ContextComponent
from pepper.framework.abstract.statistics import StatisticsComponent
from pepper.framework.abstract.monitoring import MonitoringComponent
from pepper.knowledge import animations

"""
HOWTO

1. (Re)Start Docker
2. Start Object Detection pepper_tensorflow/pepper_tensorflow/object_detection.py
3. Start This script!

"""


class BroaderMindApp(ApplicationContainer,
                     AbstractApplication,
                     StatisticsComponent,           # Show Performance Statistics in Terminal
                     MonitoringComponent,           # Display what Robot (or Computer) sees in browser
                     ContextComponent,              # Context (dependency of MonitoringComponent)
                     ObjectDetectionComponent,      # Object Detection (dependency of MonitoringComponent)
                     FaceRecognitionComponent,      # Face Recognition (dependency of MonitoringComponent)
                     SpeechRecognitionComponent,    # Speech Recognition Component (dependency)
                     TextToSpeechComponent):        # Text to Speech (dependency)

    def __init__(self):
        super(BroaderMindApp, self).__init__()

        self.context.start_chat("Human")

    def on_chat_turn(self, utterance):

        # TODO: Change animation to preferred animation
        self.say('hello! ... ...', animation=animations.AFFIRMATIVE)


if __name__ == '__main__':
    BroaderMindApp().run()
