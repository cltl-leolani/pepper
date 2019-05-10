from .responder import Responder, ResponderType

from pepper.framework import *
from pepper.language import Utterance
from pepper.knowledge import animations, QnA
from pepper import config

from typing import Optional, Union, Tuple, Callable

from random import choice


class VisionResponder(Responder):

    SEE_OBJECT = [
        "what do you see",
        "what can you see",
        "what did you see",
        "what have you seen"
    ]

    SEE_PERSON = [
        "who do you see",
        "who can you see",
    ]

    SEE_PERSON_ALL = [
        "who did you see",
        "who have you seen"
    ]

    SEE_SPECIFIC = [
        "do you see",
        "can you see"
    ]

    I_SEE = [
        "I see",
        "I can see",
        "I think I see",
        "I observe",
    ]

    I_SAW = [
        "I saw",
        "I have seen",
        "I think I observed"
    ]

    NO_OBJECT = [
        "I don't see anything",
        "I don't see any object",
    ]

    NO_PEOPLE = [
        "I don't see anybody I know",
        "I don't see familiar faces",
        "I cannot identify any of my friends",
    ]

    @property
    def type(self):
        return ResponderType.Sensory

    @property
    def requirements(self):
        return [TextToSpeechComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]

        objects = [obj.name for obj in utterance.chat.context.objects]
        people = [p.name for p in utterance.chat.context.people]

        all_people = [p.name for p in utterance.chat.context.all_people]

        # Enumerate Currently Visible Objects
        if utterance.transcript.lower() in self.SEE_OBJECT:
            if objects:
                return 1, lambda: app.say("{} {}".format(choice(self.I_SEE), self._objects_to_sequence(objects)))
            else:
                return 0.5, lambda: app.say(choice(self.NO_OBJECT))

        # Enumerate Currently Visible People
        elif utterance.transcript.lower() in self.SEE_PERSON:
            if people:
                return 1, lambda: app.say("{} {}".format(choice(self.I_SEE), self._people_to_sentence(people)))
            else:
                return 0.5, lambda: app.say(choice(self.NO_PEOPLE))

        # Enumerate All Observed People
        elif utterance.transcript.lower() in self.SEE_PERSON_ALL:
            if all_people:
                return 1, lambda: app.say("{} {}".format(choice(self.I_SAW), self._people_to_sentence(all_people)))
            else:
                return 0.5, lambda: app.say(choice(self.NO_PEOPLE))

        # Respond to Individual Object/Person Queries
        else:

            items = objects + people

            response = []

            for cue in self.SEE_SPECIFIC:
                if cue in utterance.transcript.lower():
                    for item in items:
                        if item.lower() in utterance.transcript.lower():
                            response.append(item)

            if response:
                return 1.0, lambda: app.say("Yes, I can see " + self._people_to_sentence(response))

    @staticmethod
    def _insert_a_an(word):
        if word[0] in "euioa":
            return "an {}".format(word)
        else:
            return "a {}".format(word)

    @staticmethod
    def _objects_to_sequence(objects):
        object_count = {}

        for obj in objects:
            if not obj in object_count:
                object_count[obj] = 0

            object_count[obj] += 1

        items = [(name + ("s" if count > 1 else ""), count) for name, count in object_count.items()]

        if len(items) == 1:
            return "{} {}".format(items[1], items[0])
        else:
            return "{} and {}.".format(", ".join("{} {}".format(i[1], i[0]) for i in items[:-1]),
                                       "{} {}".format(items[-1][1], items[-1][0]))

    @staticmethod
    def _people_to_sentence(people):
        if len(people) == 1:
            return people[0]
        else:
            return "{} and {}.".format(", ".join(people[:-1]), people[-1])


class PreviousUtteranceResponder(Responder):

    CUE = [
        "what did you say",
        "i didn't hear you",
        "i can't hear you",
        "come again",
        "excuse me",
    ]

    REPEAT = "I said:"

    @property
    def type(self):
        return ResponderType.Sensory

    @property
    def requirements(self):
        return [TextToSpeechComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]
        for cue in self.CUE:
            if cue in utterance.transcript.lower():
                for u in utterance.chat.utterances[:-1][::-1]:
                    if u.me and not u.transcript.startswith(self.REPEAT):
                        return 1.0, lambda: app.say(text="{} {}".format(self.REPEAT, u.transcript),
                                                    animation=animations.EXPLAIN)
                return 1.0, lambda: app.say("I didn't say anything yet...")


class LocationResponder(Responder):

    CUE_FULL = [
        "where are we",
        "where are you",
        "where we are",
        "where you are",
        "what is here",
    ]

    @property
    def type(self):
        return ResponderType.Sensory

    @property
    def requirements(self):
        return [TextToSpeechComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]
        if utterance.transcript.lower() in self.CUE_FULL:
            return 1, lambda: app.say(self._location_to_text(utterance.chat.context.location))

    @staticmethod
    def _location_to_text(location):
        return "We're in {}, {}, {}.".format(location.city, location.region, location.country)


class TimeResponder(Responder):

    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    MONTHS = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]

    DATE = [
        "What day is it",
    ]

    @property
    def type(self):
        return ResponderType.Sensory

    @property
    def requirements(self):
        return [TextToSpeechComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]

        if utterance.transcript.lower() in self.DATE:
            dt = utterance.context.datetime

            return 1, lambda: app.say("Today is {}, {} {}, {}!".format(
                self.DAYS[dt.weekday()], self.MONTHS[dt.month-1], dt.day, dt.year
            ))


class IdentityResponder(Responder):

    CUE_ME = [
        "who are you",
        "what is your name",
    ]

    ANSWER_ME = [
        "My name is",
        "I'm",
    ]

    CUE_YOU = [
        "who am i ",
        "what is my name"
    ]

    ANSWER_YOU = [
        "Your name is",
        "You are"
    ]

    @property
    def type(self):
        return ResponderType.Sensory

    @property
    def requirements(self):
        return [TextToSpeechComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]
            if utterance.transcript.lower() in self.CUE_ME:
                return 1.0, lambda: app.say("{} {}!".format(choice(self.ANSWER_ME), config.NAME))

            if utterance.transcript.lower() in self.CUE_YOU:
                return 1.0, lambda: app.say("{} {}!".format(choice(self.ANSWER_YOU), utterance.chat.speaker))
