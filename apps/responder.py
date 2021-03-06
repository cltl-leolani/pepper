

import os
from random import choice
from time import time

import numpy as np
from typing import List, Callable

from pepper.app_container import ApplicationContainer, Application
from pepper.framework.application.brain import BrainComponent
from pepper.framework.application.context import ContextComponent
from pepper.framework.application.display import DisplayComponent
# noinspection PyUnresolvedReferences
from pepper.framework.application.exploration import ExplorationComponent
from pepper.framework.application.face_detection import FaceRecognitionComponent
from pepper.framework.application.intention import AbstractIntention
# noinspection PyUnresolvedReferences
from pepper.framework.application.monitoring import MonitoringComponent
from pepper.framework.application.motion import MotionComponent
from pepper.framework.application.object_detection import ObjectDetectionComponent
from pepper.framework.application.speech_recognition import SpeechRecognitionComponent
from pepper.framework.application.statistics import StatisticsComponent
# noinspection PyUnresolvedReferences
from pepper.framework.application.subtitles import SubtitlesComponent
from pepper.framework.application.text_to_speech import TextToSpeechComponent
# TODO move constants from Openface into a configuration
from pepper.framework.sensor.api import FaceDetector
from pepper.framework.sensor.face import FaceClassifier
from pepper.knowledge import sentences
from pepper.responder import *

IMAGE_VU = "https://www.vu.nl/nl/Images/VUlogo_NL_Wit_HR_RGB_tcm289-201376.png"

RESPONDERS = [
    VisionResponder(), PreviousUtteranceResponder(), IdentityResponder(), LocationResponder(), TimeResponder(),
    QnAResponder(),
    GreetingResponder(), GoodbyeResponder(), ThanksResponder(), AffirmationResponder(), NegationResponder(),
    WikipediaResponder(), WolframResponder(), # TODO: (un)comment to turn factual responder On/Off
    BrainResponder(),
    UnknownResponder(),
]


class ResponderIntention(ApplicationContainer,
                         AbstractIntention, StatisticsComponent,
                         # SubtitlesComponent,  # TODO: (un)comment to turn tablet subtitles On/Off
                         MonitoringComponent,  # TODO: (un)comment to turn Web View On/Off
                         # WikipediaResponder, # WolframResponder,   # TODO:(un)comment to turn factual responder On/Off
                         ExplorationComponent,  # TODO: (un)comment to turn exploration On/Off
                         ContextComponent,
                         ObjectDetectionComponent, FaceRecognitionComponent,
                         SpeechRecognitionComponent, TextToSpeechComponent,
                         BrainComponent,
                         MotionComponent, DisplayComponent):

    def __init__(self):
        super(ResponderIntention, self).__init__()


class DefaultIntention(ResponderIntention):
    IGNORE_TIMEOUT = 60

    def __init__(self):
        super(DefaultIntention, self).__init__()

        self._ignored_people = {}
        self.response_picker = ResponsePicker(self, RESPONDERS + [MeetIntentionResponder()])

    def start(self):
        super(DefaultIntention, self).start()
        self.show_on_display(IMAGE_VU)

    def on_chat_enter(self, name):
        self._ignored_people = {n: t for n, t in list(self._ignored_people.items()) if time() - t < self.IGNORE_TIMEOUT}

        if name not in self._ignored_people:
            self.context.start_chat(name)
            self.say("{}, {}".format(choice(sentences.GREETING), name))

    def on_chat_exit(self):
        self.say("{}, {}".format(choice(sentences.GOODBYE), self.context.chat.speaker))
        self.context.stop_chat()

    def on_chat_turn(self, utterance):
        super(DefaultIntention, self).on_chat_turn(utterance)

        responder = self.response_picker.respond(utterance)

        if isinstance(responder, MeetIntentionResponder):
            self.change_intention(MeetIntention())

        elif isinstance(responder, GoodbyeResponder):
            self._ignored_people[utterance.chat.speaker] = time()
            self.context.stop_chat()


# TODO: What are you thinking about? -> Well, Bram, I thought....

class BinaryQuestionIntention(ResponderIntention):
    NEGATION = NegationResponder
    AFFIRMATION = AffirmationResponder

    def __init__(self, question, callback, responders):
        # type: (List[str], Callable[[bool], None], List[Responder]) -> None
        super(BinaryQuestionIntention, self).__init__()

        self.question = question
        self.callback = callback

        # Add Necessary Responders if not already included
        for responder_class in [self.NEGATION, self.AFFIRMATION]:
            if not responder_class in [responder.__class__ for responder in responders]:
                responders.append(responder_class())

        self.response_picker = ResponsePicker(self, responders)

    def start(self):
        super(BinaryQuestionIntention, self).start()
        self.say(choice(self.question))

    def on_chat_turn(self, utterance):
        responder = self.response_picker.respond(utterance)

        if isinstance(responder, self.AFFIRMATION):
            self.callback(True)
        elif isinstance(responder, self.NEGATION):
            self.callback(False)
        else:
            self.say(choice(self.question))


class MeetIntention(ResponderIntention):
    CUES = ["my name is", "i am", "no my name is", "no i am"]

    def __init__(self):
        super(MeetIntention, self).__init__()

        self._friends_dir = self.config_manager.get_config("DEFAULT").get("people_friends_dir")
        self._new_dir = self.config_manager.get_config("DEFAULT").get("people_new_dir")

        self.response_picker = ResponsePicker(self, RESPONDERS)

        self._asrs = [self.asr(language) for language in ['nl-NL', 'es-ES']]

        self._last_statement_was_name = False
        self._current_name = None
        self._possible_names = {}
        self._denied_names = set()

    def start(self):
        super(MeetIntention, self).start()

        self.context.start_chat("Stranger")

        self.say("{} {}".format(choice(sentences.INTRODUCE), choice(sentences.ASK_NAME)))

    def on_chat_exit(self):
        self.context.stop_chat()
        self.change_intention(DefaultIntention())

    def on_transcript(self, hypotheses, audio):
        self._last_statement_was_name = False

        if self._is_name_statement(hypotheses):

            # Parse Audio using Multiple Languages!
            for asr in self._asrs:
                hypotheses.extend(asr.transcribe(audio))

            for hypothesis in hypotheses:

                self._last_statement_was_name = True

                name = hypothesis.transcript.split()[-1]

                # If not already denied
                if name not in self._denied_names and name[0].isupper():

                    # Update possible names with this name
                    if name not in self._possible_names:
                        self._possible_names[name] = 0.0
                    self._possible_names[name] += hypothesis.confidence

            self._current_name = self._get_current_name()

            # If hypotheses about just mentioned name exist -> Ask Verification
            if self._last_statement_was_name and self._current_name:
                self.say(choice(sentences.VERIFY_NAME).format(self._current_name))

    def on_chat_turn(self, utterance):

        # If not already responded to Name Utterance
        if not self._last_statement_was_name:

            # Respond Normally to Whatever Utterance
            responder = self.response_picker.respond(utterance)

            if self._current_name:  # If currently verifying a name

                # If negated, remove name from name hypotheses (and suggest alternative)
                if isinstance(responder, NegationResponder):
                    self._denied_names.add(self._current_name)
                    self._possible_names.pop(self._current_name)
                    self._current_name = self._get_current_name()

                    # Try to Verify next best hypothesis
                    self.say(choice(sentences.VERIFY_NAME).format(self._current_name))

                # If confirmed, store name and start chat with person
                elif isinstance(responder, AffirmationResponder):
                    self.say(choice(sentences.JUST_MET).format(self._current_name))

                    # Save New Person to Memory
                    self._save()

                    # Start new chat and switch intention
                    self.context.start_chat(self._current_name)
                    self.change_intention(DefaultIntention())

                # Exit on User Goodbye
                elif isinstance(responder, GoodbyeResponder):
                    self.change_intention(DefaultIntention())

                else:  # If some other question was asked, remind human of intention
                    self.say(choice(sentences.VERIFY_NAME).format(self._current_name))

            else:  # If no name hypothesis yet exists
                self.say("But, {}".format(choice(sentences.ASK_NAME)))

    def _get_current_name(self):
        if self._possible_names:
            return [n for n, c in sorted(list(self._possible_names.items()), key=lambda i: i[1], reverse=True)][0]

    def _is_name_statement(self, hypotheses):
        for hypothesis in hypotheses:
            for cue in self.CUES:
                if cue in hypothesis.transcript.lower():
                    return True
        return False

    def _save(self):
        # TODO get face_vectors from context or somewhere else
        face_vectors = self.context.current_people(in_chat=True, timeout=10)
        name, features = self._current_name, np.concatenate(face_vectors).reshape(-1, FaceDetector.FEATURE_DIM)

        if name != FaceClassifier.NEW:  # Prevent Overwrite of NEW.bin
            self.face_classifier.add(name, features)
            features.tofile(os.path.join(self._new_dir, "{}.bin".format(name)))


if __name__ == '__main__':
    Application(DefaultIntention()).run()
