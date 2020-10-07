import logging
import random
from threading import Lock
from time import time

import numpy as np

from pepper.framework.context.api import TOPIC_ON_CHAT_ENTER, TOPIC_ON_CHAT_EXIT
from pepper.framework.multiprocessing import TopicWorker, RejectionStrategy
from pepper.framework.resource.api import acquire
from pepper.framework.sensor.api import ObjectDetector, FaceDetector
from pepper.framework.sensor.asr import AbstractASR

logger = logging.getLogger(__name__)


class ExplorationWorker(TopicWorker):
    """
    Explore Environment to keep up to date on the people/objects inhabiting it.
    """

    TIMEOUT = 15
    LAST_MOVE = 0
    SPEED = 0.05

    TOPICS = [ObjectDetector.TOPIC, FaceDetector.TOPIC, AbstractASR.TOPIC]

    def __init__(self, name, event_bus):
        super(ExplorationWorker, self).__init__(ExplorationWorker.TOPICS, event_bus, name=name,
                                                interval = 1, scheduled = True,
                                                buffer_size=1, rejection_strategy=RejectionStrategy.DROP)

        self._chat_lock = Lock()
        
    def start(self):
        self.event_bus.subscribe(TOPIC_ON_CHAT_ENTER, self.__on_chat_enter())
        self.event_bus.subscribe(TOPIC_ON_CHAT_EXIT, self.__on_chat_exit())
        super(ExplorationWorker, self).start()

    def stop(self):
        self.event_bus.unsubscribe(TOPIC_ON_CHAT_ENTER, self.__on_chat_enter())
        self.event_bus.unsubscribe(TOPIC_ON_CHAT_EXIT, self.__on_chat_exit())
        super(ExplorationWorker, self).stop()

    def __on_chat_enter(self, event):
        self.__chat_lock.acquire()

    def __on_chat_enter(self, event):
        self.__chat_lock.release()

    def __on_event(self, event):
        # type: (Event) -> None
        with acquire(self.__chat_lock, blocking=False) as locked:
            if locked:
                # At a certain interval
                if time() - ExplorationWorker.LAST_MOVE > ExplorationWorker.TIMEOUT:
                    self.explore()  # Explore!
                    ExplorationWorker.LAST_MOVE = time()

    def __explore(self):
        # type: () -> None
        """Explore Environment to keep up to date on the people/objects inhabiting it."""

        # Get Observations, sorted (high to low) by last time seen
        observations = sorted(self.context.context.objects, key=lambda obj: obj.time)

        # If there are any observations and the odds are in this if statement's favour
        if observations and random.random() > 0.33333:
            # Look at least recently seen object's last known location
            self._log.debug("Look at {}".format(observations[0]))
            self.backend.motion.look(observations[0].direction, ExplorationWorker.SPEED)
        else:
            # Look at random point to keep exploring environment
            self._log.debug("Look at random point")
            self.backend.motion.look((
                float(np.clip(np.random.standard_normal() / 3 * np.pi / 2, -np.pi, np.pi)),
                float(np.clip(np.pi / 2 + np.random.standard_normal() / 10 * np.pi, 0, np.pi))
            ), ExplorationWorker.SPEED)
