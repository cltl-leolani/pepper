import logging
import random
from threading import Lock
from time import time

import numpy as np

from pepper.framework.backend.abstract.motion import TOPIC_LOOK
from pepper.framework.context.api import TOPIC_ON_CHAT_ENTER, TOPIC_ON_CHAT_EXIT, Context
from pepper.framework.infra.event.api import Event, EventBus
from pepper.framework.infra.multiprocessing import TopicWorker, RejectionStrategy
from pepper.framework.infra.resource.api import acquire
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

    TOPICS = [ObjectDetector.TOPIC, FaceDetector.TOPIC, AbstractASR.TOPIC,
              TOPIC_ON_CHAT_ENTER, TOPIC_ON_CHAT_EXIT]

    def __init__(self, context, name, event_bus):
        # type: (Context, str, EventBus) -> None
        super(ExplorationWorker, self).__init__(ExplorationWorker.TOPICS, event_bus, name=name,
                                                interval = 0, scheduled = 1,
                                                buffer_size=1, rejection_strategy=RejectionStrategy.DROP)
        self._context = context
        self._chat_lock = Lock()
        
    def process(self, event):
        # type: (Event) -> None
        if not event:
            # Only explore if we are not in a chat
            with acquire(self._chat_lock, blocking=False) as locked:
                if locked:
                    # At a certain interval
                    if time() - ExplorationWorker.LAST_MOVE > ExplorationWorker.TIMEOUT:
                        self.explore()  # Explore!
                        ExplorationWorker.LAST_MOVE = time()
        elif TOPIC_ON_CHAT_ENTER == event.metadata.topic:
            self._chat_lock.acquire()
        elif TOPIC_ON_CHAT_EXIT == event.metadata.topic:
            self._chat_lock.release()

    def explore(self):
        # type: () -> None
        """Explore Environment to keep up to date on the people/objects inhabiting it."""

        # Get Observations, sorted (high to low) by last time seen
        observations = sorted(self._context.objects, key=lambda obj: obj.time)

        # If there are any observations and the odds are in this if statement's favour
        if observations and random.random() > 0.33333:
            # Look at least recently seen object's last known location
            logger.debug("Look at {}".format(observations[0]))
            event = Event({'direction': observations[0].direction, 'speed': ExplorationWorker.SPEED}, None)
        else:
            # Look at random point to keep exploring environment
            logger.debug("Look at random point")

            direction = (
                float(np.clip(np.random.standard_normal() / 3 * np.pi / 2, -np.pi, np.pi)),
                float(np.clip(np.pi / 2 + np.random.standard_normal() / 10 * np.pi, 0, np.pi))
            )
            event = Event({'direction': direction, 'speed': ExplorationWorker.SPEED}, None)
        self.event_bus.publish(TOPIC_LOOK, event)
