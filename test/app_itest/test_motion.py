import logging
import sys
import unittest

import numpy as np

from pepper.framework.application.application import AbstractApplication
from pepper.framework.application.intention import AbstractIntention
from pepper.framework.application.motion import MotionComponent
from pepper.framework.backend.abstract.backend import AbstractBackend
from pepper.framework.backend.abstract.motion import AbstractMotion
from pepper.framework.backend.container import BackendContainer
from pepper.framework.infra.di_container import singleton, DIContainer
from pepper.framework.infra.event.api import EventBusContainer
from pepper.framework.infra.event.memory import SynchronousEventBusContainer
from pepper.framework.infra.resource.threaded import ThreadedResourceContainer
from test import util



class TestBackendContainer(BackendContainer, EventBusContainer):
    def __init__(self):
        super(TestBackendContainer, self).__init__()

    @property
    @singleton
    def backend(self):
        return TestBackend(self.event_bus, self.resource_manager)


class TestMotion(AbstractMotion):
    def __init__(self, event_bus, resource_manager):
        super(TestMotion, self).__init__(event_bus, resource_manager)
        self.looks = []
        self.points = []

    def look(self, direction, speed=1):
        self.looks.append(direction)

    def point(self, direction, speed=1):
        self.points.append(direction)


class TestBackend(AbstractBackend):
    def __init__(self, event_bus, resource_manager):
        super(TestBackend, self).__init__(motion=TestMotion(event_bus, resource_manager),
                                          camera=None, microphone=None, text_to_speech=None, led=None, tablet=None)


class ApplicationContainer(TestBackendContainer, SynchronousEventBusContainer, ThreadedResourceContainer):
    def __init__(self):
        super(ApplicationContainer, self).__init__()


class TestIntention(ApplicationContainer, AbstractIntention, MotionComponent):
    def __init__(self):
        super(TestIntention, self).__init__()


class TestApplication(AbstractApplication, ApplicationContainer):
    def __init__(self, intention):
        super(TestApplication, self).__init__(intention)


class MotionITest(unittest.TestCase):
    def setUp(self):
        self.intention = TestIntention()
        self.application = TestApplication(self.intention)
        self.application.start()

    def tearDown(self):
        self.application.stop()
        del self.application
        DIContainer._singletons.clear()

    def test_point(self):
        self.intention.point((1.0, 2.0), 3.0)

        util.await(lambda: len(self.intention.backend.motion.points) > 0, msg="point event")

        points = self.intention.backend.motion.points
        self.assertEqual(1, len(points))
        np.testing.assert_array_equal((1.0, 2.0), points[0])

        try:
            util.await(lambda: len(self.intention.backend.motion.points) > 1, max=5)
        except unittest.TestCase.failureException:
            # Expect no more audio events
            pass

    def test_look(self):
        self.intention.look((1.0, 2.0), 3.0)

        util.await(lambda: len(self.intention.backend.motion.looks) > 0, msg="point event")

        looks = self.intention.backend.motion.looks
        self.assertEqual(1, len(looks))
        np.testing.assert_array_equal((1.0, 2.0), looks[0])

        try:
            util.await(lambda: len(self.intention.backend.motion.looks) > 1, max=5)
        except unittest.TestCase.failureException:
            # Expect no more audio events
            pass


if __name__ == '__main__':
    unittest.main()