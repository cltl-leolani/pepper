"""Example Application that shows how to work with different Intentions in one Application"""

from time import sleep

from pepper.app_container import ApplicationContainer, Application
from pepper.framework.application.face_detection import FaceRecognitionComponent
from pepper.framework.application.intention import AbstractIntention
from pepper.framework.application.speech_recognition import SpeechRecognitionComponent
from pepper.framework.application.statistics import StatisticsComponent
from pepper.framework.application.text_to_speech import TextToSpeechComponent


class BaseIntention(ApplicationContainer,
                    AbstractIntention,
                    StatisticsComponent,            # Show Performance Statistics
                    FaceRecognitionComponent,       # Face Recognition
                    SpeechRecognitionComponent,     # Speech Recognition
                    TextToSpeechComponent):         # Text to Speech
    pass  # That's it for the main application, all logic is implemented in the Intentions


# Idle Intention (not in conversation).
# Inherits from AbstractIntention and MyApplication (specified above)
class IdleIntention(BaseIntention):

    def on_face(self, faces):
        self.log.info(faces)

    # Since MyApplication inherits from FaceRecognitionComponent, the on_face_known event, becomes available here
    def on_face_known(self, faces):
        # When known face is recognized, switch to TalkIntention (now we're in conversation!)
        self.change_intention(TalkIntention(faces[0].name))


# Talk Intention (in conversation!).
# Inherits from AbstractIntention and MyApplication (specified above)
class TalkIntention(BaseIntention):

    # Called when Intention is Initialized
    def __init__(self, speaker):
        super(TalkIntention, self).__init__()

        # Save Speaker, to refer to it later!
        self._speaker = speaker

        # Greet Recognized human by name
        self.say("Hello, {}!".format(self._speaker))

    # Called when Human has uttered some sentence
    def on_transcript(self, hypotheses, audio):

        # If Human ends conversation, switch back to Idle Intention
        for hypothesis in hypotheses:

            self.log.debug(hypothesis)

            if hypothesis.transcript.lower() in ["bye bye", "bye", "goodbye", "see you"]:
                # Respond Goodbye, <speaker>!
                self.say("Goodbye, {}!".format(self._speaker))

                # Sleep 5 seconds (else human would be instantly greeted again)
                sleep(5)

                # Switch Back to Idle Intention
                self.change_intention(IdleIntention())

                return
        else:

            # If Human doesn't end the conversation,
            # act as if you understand what he/she is saying :)
            self.say("How interesting!")


if __name__ == '__main__':
    Application(IdleIntention()).run()
