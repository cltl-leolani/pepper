"""Example Application that displays what it sees in the browser"""

from pepper.app_container import ApplicationContainer
from pepper.framework.abstract.application import AbstractApplication
from pepper.framework.abstract.object_detection import ObjectDetectionComponent
from pepper.framework.abstract.text_to_speech import TextToSpeechComponent
from pepper.framework.abstract.face_detection import FaceRecognitionComponent
from pepper.framework.abstract.speech_recognition import SpeechRecognitionComponent
from pepper.framework.abstract.context import ContextComponent
from pepper.framework.component import StatisticsComponent, DisplayComponent, SceneComponent


class DisplayApp(ApplicationContainer,
                 AbstractApplication,           # Each Application inherits from AbstractApplication
                 StatisticsComponent,           # Show Performance Statistics in Terminal
                 DisplayComponent,              # Display what Robot (or Computer) sees in browser
                 SceneComponent,                # Scene (dependency of DisplayComponent)
                 ContextComponent,              # Context (dependency of DisplayComponent)
                 ObjectDetectionComponent,      # Object Detection (dependency of DisplayComponent)
                 FaceRecognitionComponent,      # Face Recognition (dependency of DisplayComponent)
                 SpeechRecognitionComponent,    # Speech Recognition Component (dependency)
                 TextToSpeechComponent):        # Text to Speech (dependency)

    pass  # Application does not need to react to events :)


if __name__ == '__main__':
    DisplayApp().run()
