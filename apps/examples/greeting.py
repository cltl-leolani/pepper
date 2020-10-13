"""Example Application that greets known and unknown people"""

from time import time

from pepper.app_container import ApplicationContainer, Application
from pepper.framework.application.face_detection import FaceRecognitionComponent
from pepper.framework.application.intention import AbstractIntention
from pepper.framework.application.speech_recognition import SpeechRecognitionComponent
from pepper.framework.application.statistics import StatisticsComponent
from pepper.framework.application.text_to_speech import TextToSpeechComponent


class GreetingIntention(ApplicationContainer,
                        AbstractIntention,
                        FaceRecognitionComponent,     # We need Face Recognition to Greet People by Name
                        StatisticsComponent,
                        SpeechRecognitionComponent,
                        TextToSpeechComponent):       # We need Text to Speech to actually greet people

    GREET_TIMEOUT = 15  # Only Greet people once every X seconds

    def __init__(self):
        """Greets New and Known People"""
        super(GreetingIntention, self).__init__()

        self.name_time = {}  # Dictionary of <name, time> pairs, to keep track of who is greeted when

    def on_face_known(self, faces):
        """
        On Person Event.
        Called every time a known face is detected.
        """

        for person in faces:
            if self.is_greeting_appropriate(person.name):
                self.say("Hello, {}!".format(person.name))

    def on_face_new(self, faces):
        """
        On New Person Event.
        Called every time an unknown face is detected.
        """

        if self.is_greeting_appropriate("new"):
            self.say("I see a new person!, Hello stranger!")

    def is_greeting_appropriate(self, name):
        """Returns True if greeting is appropriate and updates Greeting Time"""

        # Appropriateness arises when
        #  1. person hasn't been seen before, or
        #  2. enough time has passed since last sighting
        if name not in self.name_time or (time() - self.name_time[name]) > self.GREET_TIMEOUT:

            # Store last seen time (right now) in name_time dictionary
            self.name_time[name] = time()

            # Return "Appropriate"
            return True

        # Return "Not Appropriate"
        return False


if __name__ == "__main__":
    Application(GreetingIntention()).run()
