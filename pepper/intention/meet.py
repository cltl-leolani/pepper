from pepper.framework import AbstractIntention
from pepper.framework.system import SystemApp
from pepper.framework.naoqi import NaoqiApp
from pepper.language.names import NameParser
from pepper.knowledge import sentences

from random import choice
from time import sleep
from enum import Enum



class MeetAction(Enum):
    LISTENING_FOR_NAME = 0
    VERIFYING_NAME = 1


class MeetIntention(AbstractIntention):

    MIN_SAMPLES = 25

    def __init__(self, app):
        super(MeetIntention, self).__init__(app)

        self._name_parser = NameParser(list(self.app.faces.keys()))

        self._name = None
        self._face = []

        self._action = MeetAction.LISTENING_FOR_NAME

        self.say("{} {} {}".format(
            choice(sentences.GREETING),
            choice(sentences.INTRODUCE),
            choice(sentences.ASK_NAME)))

    def on_face(self, bounds, face):
        self._face.append(face)

    def on_transcript(self, transcript, audio):
        if self._action == MeetAction.LISTENING_FOR_NAME:

            # Try to parse name
            self.say(choice(sentences.THINKING))
            parsed_name = self._name_parser.parse_new(audio)

            # If name was heard, ask person to verify it
            if parsed_name:
                self._name, confidence = parsed_name
                self.say(choice(sentences.VERIFY_NAME).format(self._name))
                self._action = MeetAction.VERIFYING_NAME

            # If no name was heard, kindly ask person to repeat it
            else:
                self.say("{} {}".format(
                    choice(sentences.DIDNT_HEAR_NAME),
                    choice(sentences.REPEAT_NAME)))

        # If a name was heard, make sure to verify
        elif self._action == MeetAction.VERIFYING_NAME:
            text, confidence = transcript[0]
            for word in text.split():
                # If affirmation was heard
                if word in sentences.AFFIRMATION:
                    # And enough face samples have been gathered
                    if len(self._face) < self.MIN_SAMPLES:
                        self.say("{} {}".format(
                            choice(sentences.JUST_MET).format(self._name),
                            choice(sentences.MORE_FACE_SAMPLES)))
                        while len(self._face) < self.MIN_SAMPLES:
                            sleep(1)
                        self.say(choice(sentences.THANK))

                    # The meeting is official!
                    self.say("{} {}".format(
                        choice(sentences.HAPPY),
                        choice(sentences.JUST_MET).format(self._name)))
                    return

                # If negation was heard, listen for name again.
                elif word in sentences.NEGATION:

                    # Catch sentences that include both a name and a negation
                    parsed_name = self._name_parser.parse_new(audio)
                    if parsed_name and parsed_name[1] > 0.8:
                        self._name, confidence = parsed_name
                        self.say("{} {}".format(
                            choice(sentences.UNDERSTAND),
                            choice(sentences.VERIFY_NAME).format(self._name)))

                    # Else ask person to repeat name
                    else:
                        self.say("{} {}".format(
                            choice(sentences.SORRY),
                            choice(sentences.REPEAT_NAME)))
                        self._action = MeetAction.LISTENING_FOR_NAME
                    return


if __name__ == '__main__':
    # Boot Application
    # app = SystemApp()  # Run on PC
    app = NaoqiApp()  # Run on Robot

    # Boot Intention
    intention = MeetIntention(app)

    # Link Intention to App
    app.intention = intention

    # Start App (a.k.a. Start Microphone and Camera)
    app.start()