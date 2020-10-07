from time import time

import numpy as np
from typing import List

from pepper import config
from pepper.framework.backend.abstract.text_to_speech import TOPIC as TTS_TOPIC
from pepper.framework.config.api import ConfigurationManager
from pepper.framework.context.api import TOPIC_ON_CHAT_ENTER, TOPIC_ON_CHAT_EXIT, TOPIC_ON_CHAT_TURN, Context
from pepper.framework.event.api import Event, EventBus
from pepper.framework.multiprocessing import TopicWorker, RejectionStrategy
from pepper.framework.resource.api import ResourceManager
from pepper.framework.sensor.api import Object, ObjectDetector, FaceDetector
from pepper.framework.sensor.asr import AbstractASR, UtteranceHypothesis
from pepper.framework.sensor.face import Face

TOPICS = [ObjectDetector.TOPIC, FaceDetector.TOPIC, AbstractASR.TOPIC, TTS_TOPIC]


class ContextWorker(TopicWorker):
    # Minimum Distance of Person to Enter/Exit Conversation
    PERSON_AREA_ENTER = 0.25
    PERSON_AREA_EXIT = 0.2

    # Minimum Distance Difference of Person to Enter/Exit Conversation
    PERSON_DIFF_ENTER = 1.5
    PERSON_DIFF_EXIT = 1.1

    def __init__(self, context, name, event_bus, resource_manager, config_manager):
        # type: (Context, str, EventBus, ResourceManager, ConfigurationManager) -> None
        super(ContextWorker, self).__init__(TOPICS, event_bus, interval=0, scheduled=1, name=name,
                                            buffer_size=32, rejection_strategy=RejectionStrategy.DROP,
                                            resource_manager=resource_manager, requires=TOPICS,
                                            provides=[TOPIC_ON_CHAT_ENTER, TOPIC_ON_CHAT_TURN, TOPIC_ON_CHAT_EXIT])
        self.context = context

        configuration = config_manager.get_config("pepper.framework.component.context")
        self._conversation_timeout = configuration.get_float("conversation_timeout")
        self._conversation_time = time()

        self._people_info = []

    def process(self, event):
        if not event:
            self.process_scheduled()
        elif ObjectDetector.TOPIC == event.metadata.topic:
            self.process_object(event.payload)
        elif FaceDetector.TOPIC == event.metadata.topic:
            self.process_face(event.payload)
        elif AbstractASR.TOPIC == event.metadata.topic:
            self.process_transcript(event.payload['hypotheses'])
        elif TTS_TOPIC == event.metadata.topic:
            self.process_utterance(event.payload['text'])

    def process_scheduled(self):
        # Get People within Conversation Bounds
        closest_people = self.get_closest_people()
        current_faces = self.context.current_people(timeout=5)

        if not self.context.chatting:
            # If one person is closest and his/her face is identifiable -> Start One-on-One Conversation
            if len(closest_people) == 1:
                closest_person = closest_people[0]
                # TODO there is a timing issue here, we might already have detected the object, but not the face yet
                closest_face = self.get_face_of_person(closest_person, current_faces)

                if closest_face:
                    self.enter_chat(closest_face.name)

            # If multiple people are in range, with nobody seemingly closest -> Start Group Conversation
            elif len(closest_people) >= 2:
                self.enter_chat(config.HUMAN_CROWD)

        elif self.context.chatting:
            # When talking to a Group
            if self.context.chat.speaker == config.HUMAN_CROWD:

                # If still in conversation with Group, update conversation time (and thus continue conversation)
                if len(closest_people) >= 2:
                    self._conversation_time = time()

                # Else, when Group Conversation times out
                elif time() - self._conversation_time >= self._conversation_timeout:

                    # If a single Person enters conversation at this point -> Start conversation with them
                    if len(closest_people) == 1:
                        closest_face = self.get_face_of_person(closest_people[0], current_faces)

                        if closest_face:
                            self.enter_chat(closest_face.name)
                    else:
                        self.exit_chat()

            else:  # When talking to a specific Person
                # If still in conversation with Person, update conversation time (and thus continue conversation)
                if len(closest_people) == 1:
                    closest_face = self.get_face_of_person(closest_people[0], current_faces)

                    if closest_face:
                        # If Still Chatting with Same Person -> Update Conversation Time & Face Vectors
                        # Also continue when person is "NEW", to combat "Hello Stranger" mid conversation...
                        if closest_face.name in [self.context.chat.speaker, Face.UNKNOWN]:
                            self._conversation_time = time()

                        # If Chatting to Unknown Person (Stranger) and Known Person Appears -> Switch Chat to Known
                        elif self.context.chat.speaker == config.HUMAN_UNKNOWN and \
                                closest_face.name != config.HUMAN_UNKNOWN:
                            self.enter_chat(closest_face.name)

                # Else, when conversation times out with specific Person
                elif time() - self._conversation_time >= self._conversation_timeout:

                    # If another Person enters conversation at this point -> Start Conversation with them
                    if len(closest_people) == 1:
                        closest_face = self.get_face_of_person(closest_people[0], current_faces)

                        if closest_face:
                            self.enter_chat(closest_face.name)

                    # If Group enters conversation at this point -> Start Conversation with them
                    if len(closest_people) >= 2:
                        self.enter_chat(config.HUMAN_CROWD)

                    # Otherwise, exit chat with specific Person
                    else:
                        self.exit_chat()

    def enter_chat(self, name):
        self.event_bus.publish(TOPIC_ON_CHAT_ENTER, Event(name, None))
        self._conversation_time = time()

    def exit_chat(self):
        self.event_bus.publish(TOPIC_ON_CHAT_EXIT, Event(None, None))

    def process_object(self, objects):
        # type: (List[Object]) -> None
        self.context.add_objects(objects)
        self._people_info = [obj for obj in objects if obj.name == "person"]

    def process_face(self, people):
        # type: (List[Face]) -> None
        self.context.add_people(people)

    def process_transcript(self, hypotheses):
        # type: (List[UtteranceHypothesis]) -> None
        if self.context.chatting and hypotheses:
            utterance = self.context.chat.add_utterance(hypotheses, False)

            self.event_bus.publish(TOPIC_ON_CHAT_TURN, Event(utterance, None))

    def process_utterance(self, text):
        # type: (str) -> None
        if self.context.chatting:
            self.context.chat.add_utterance([UtteranceHypothesis(text, 1.0)], me=True)

    def get_face_of_person(self, person, faces):
        # type: (Object, List[Face]) -> Face
        """
        Get Face Corresponding with Person

        Persons are identified by Objects (from COCO Object Detection), while Faces are identified by OpenFace.
        This function looks at the bounding boxes of both and returns the face that corresponds with this person.

        Parameters
        ----------
        person: Object
        faces: List[Face]

        Returns
        -------
        face: Face
        """
        for face in faces:
            # TODO: Make sure face bounds are always a subset of 'person' object bounds, else: trouble imminent!
            if face.image_bounds.is_subset_of(person.image_bounds):
                return face

    def get_closest_people(self):
        # type: () -> List[Face]
        """
        Get Person or People closest to Robot (as they may be subject to conversation)

        Returns
        -------
        closest_people: List[Face]
        """
        people = self._people_info

        # To be considered 'closest' people need to make up a predefined area of the camera view
        # This area is defined differently when in conversation then when not in conversation,
        #   this removes the problems one gets when one person is right on the threshold ("hi", "bye", "hi", "bye")
        person_area_threshold = (self.PERSON_AREA_EXIT if self.context.chatting else self.PERSON_AREA_ENTER)
        people_in_range = [person for person in people if person.image_bounds.area >= person_area_threshold]

        # To be considered 'uniquely closest' a person must be closer to the next closest person
        # If this is not the case, and multiple people are close enough, a group conversation will start!
        person_diff_threshold = (self.PERSON_DIFF_EXIT if self.context.chatting else self.PERSON_DIFF_ENTER)

        # If only one person is in range
        if len(people_in_range) == 1:

            # Return that person (as a list of length 1, keeping return values consistent!)
            return [people_in_range[0]]

        # Else If multiple people are in range
        elif len(people_in_range) >= 2:
            # Sort them by proximity
            people_sorted = np.argsort([person.image_bounds.area for person in people_in_range])[::-1]

            # Identify the two closest individuals
            closest = people_in_range[people_sorted[0]]
            next_closest = people_in_range[people_sorted[1]]

            # If the closest individual is significantly (by a predefined fraction) closer than the next one
            if closest.image_bounds.area >= person_diff_threshold * next_closest.image_bounds.area:
                return [closest]
            # If people are the same distance apart
            else:
                return people_in_range
        # Else (No people are in range)
        else:
            return []
