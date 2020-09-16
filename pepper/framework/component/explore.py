import logging
import random
from time import time

import numpy as np

from pepper.framework.abstract.camera import TOPIC as CAM_TOPIC
from pepper.framework.abstract.component import AbstractComponent
from pepper.framework.component import ContextComponent

logger = logging.getLogger(__name__)


class ExploreComponent(AbstractComponent):
    """
    Explore Environment to keep up to date on the people/objects inhabiting it.
    """

    TIMEOUT = 15
    LAST_MOVE = 0
    SPEED = 0.05

    def __init__(self):
        # type: () -> None
        super(ExploreComponent, self).__init__()

        self._log.info("Initializing ExploreComponent")

        # Requires the ContextComponent to know which objects/people to look for
        context = self.require(ExploreComponent, ContextComponent)  # type: ContextComponent

        log = logger.getChild(ExploreComponent.__name__)

        def explore():
            # type: () -> None
            """Explore Environment to keep up to date on the people/objects inhabiting it."""

            # Get Observations, sorted (high to low) by last time seen
            observations = sorted(context.context.objects, key=lambda obj: obj.time)

            # If there are any observations and the odds are in this if statement's favour
            if observations and random.random() > 0.33333:
                # Look at least recently seen object's last known location
                log.debug("Look at {}".format(observations[0]))
                self.backend.motion.look(observations[0].direction, ExploreComponent.SPEED)
            else:

                # Look at random point (to keep exploring enviroment)
                log.debug("Look at random point")
                self.backend.motion.look((
                    float(np.clip(np.random.standard_normal() / 3 * np.pi/2, -np.pi, np.pi)),
                    float(np.clip(np.pi/2 + np.random.standard_normal() / 10 * np.pi, 0, np.pi))
                ), ExploreComponent.SPEED)

        def on_image(event):
            # type: (Event) -> None
            """
            Private On Image Event. Simply used because it is called n times a second.

            Parameters
            ----------
            event: Event
            """
            image = event.payload

            # When no chat is currently happening
            if not context.context.chatting:

                # At a certain interval
                if time() - ExploreComponent.LAST_MOVE > ExploreComponent.TIMEOUT:
                    explore()  # Explore!
                    ExploreComponent.LAST_MOVE = time()

        # Subscribe private on_image event to backend camera (which will call it regularly)
        self.event_bus.subscribe(CAM_TOPIC, on_image)

        self._log.info("Initialized ExploreComponent")
