"""Example Application that displays what it sees in the browser"""

from pepper.app_container import ApplicationContainer
from pepper.framework.abstract.application import AbstractApplication
from pepper.framework.abstract.object_detection import ObjectDetectionComponent
from pepper.framework.abstract.text_to_speech import TextToSpeechComponent
from pepper.framework.abstract.face_detection import FaceRecognitionComponent
from pepper.framework.abstract.speech_recognition import SpeechRecognitionComponent
from pepper.framework.abstract.context import ContextComponent
from pepper.framework.abstract.statistics import StatisticsComponent
from pepper.framework.abstract.monitoring import MonitoringComponent


class DisplayApp(ApplicationContainer,
                 AbstractApplication,           # Each Application inherits from AbstractApplication
                 StatisticsComponent,           # Show Performance Statistics in Terminal
                 MonitoringComponent,           # Display what Robot (or Computer) sees in browser
                 ContextComponent,              # Context (dependency of MonitoringComponent)
                 ObjectDetectionComponent,      # Object Detection (dependency of MonitoringComponent)
                 FaceRecognitionComponent,      # Face Recognition (dependency of MonitoringComponent)
                 SpeechRecognitionComponent,    # Speech Recognition Component (dependency)
                 TextToSpeechComponent):        # Text to Speech (dependency)

    pass  # Application does not need to react to events :)


if __name__ == '__main__':
    DisplayApp().run()
