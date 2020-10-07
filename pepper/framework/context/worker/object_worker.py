from time import time

import numpy as np
from typing import List

from pepper import config
from pepper.framework.backend.abstract.backend import AbstractBackend
from pepper.framework.context.api import TOPIC_ON_CHAT_ENTER, TOPIC_ON_CHAT_EXIT
from pepper.framework.event.api import Event
from pepper.framework.multiprocessing import TopicWorker, RejectionStrategy
from pepper.framework.sensor.api import Object, ObjectDetector
from pepper.framework.sensor.face import Face


class ContextObjectWorker(TopicWorker):
    """
    Exposes Context to Applications and contains logic to determine whether conversation should start/end.

    Parameters
    ----------
    backend: AbstractBackend
        Application Backend
    """
    # Minimum Distance of Person to Enter/Exit Conversation
    PERSON_AREA_ENTER = 0.25
    PERSON_AREA_EXIT = 0.2

    # Minimum Distance Difference of Person to Enter/Exit Conversation
    PERSON_DIFF_ENTER = 1.5
    PERSON_DIFF_EXIT = 1.1

    # TODO: Should this be a pepper.config variable? YES!
    # Number of seconds of inactivity before conversation times out
    CONVERSATION_TIMEOUT = 30

    def __init__(self, context, name, event_bus, resource_manager):
        # type: (Context, str, EventBus, ResourceManager) -> None
        super(ContextObjectWorker, self).__init__(ObjectDetector.TOPIC, event_bus, interval=0, name=name,
                                                 buffer_size=16, rejection_strategy=RejectionStrategy.DROP,
                                                 resource_manager=resource_manager,
                                                 requires=[ObjectDetector.TOPIC],
                                                 provides=[TOPIC_ON_CHAT_ENTER, TOPIC_ON_CHAT_EXIT])
        self.context = context
        self._chat_lock = resource_manager.get_write_lock(RESOURCE_CHAT)

        self._conversation_time = time()

    def process(self, event):
        # type: (Event) -> None
        """
        Parameters
        ----------
        event: Event
        """
        objects = event.payload

        self.context.add_objects(objects)
        people_info = filter(lambda obj: obj.name == "person", objects)

        # Get People within Conversation Bounds
        closest_people = self.get_closest_people(people_info)
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
                elif time() - self._conversation_time >= self.CONVERSATION_TIMEOUT:

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
                elif time() - self._conversation_time >= self.CONVERSATION_TIMEOUT:

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

    def get_closest_people(self, people):
        # type: (List[Face]) -> List[Face]
        """
        Get Person or People closest to Robot (as they may be subject to conversation)

        Parameters
        ----------
        people: List[Face]
            People, as represented by their face (id)

        Returns
        -------
        closest_people: List[Face]
        """

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

    def enter_chat(self, name):
        self.event_bus.publish(TOPIC_ON_CHAT_ENTER, Event(None, None))
        self._conversation_time = time()

    def exit_chat(self):
        self.event_bus.publish(TOPIC_ON_CHAT_EXIT, Event(None, None))



# class ContextObjectWorker(TopicWorker):
#     def __init__(self, context, name, event_bus, resource_manager):
#         # type: (Context, str, EventBus, ResourceManager) -> None
#         super(ContextObjectWorker, self).__init__(ObjectDetector.TOPIC, event_bus, interval=0, name=name,
#                                                   buffer_size=16, rejection_strategy=RejectionStrategy.BLOCK,
#                                                   resource_manager=resource_manager,
#                                                   requires=[ObjectDetector.TOPIC], provides=[])
#         self.context = context
#
#     def process(self, event):
#         # type: (Event) -> None
#         objects = event.payload
#
#         self.context.add_objects(objects)
#         self._people_info = [obj for obj in objects if obj.name == "person"]
