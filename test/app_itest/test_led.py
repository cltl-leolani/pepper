import unittest

import numpy as np

from pepper.framework.application.application import AbstractApplication
from pepper.framework.application.intention import AbstractIntention
from pepper.framework.application.led import LedComponent
from pepper.framework.backend.abstract.backend import AbstractBackend
from pepper.framework.backend.abstract.led import AbstractLed, Led
from pepper.framework.backend.container import BackendContainer
from pepper.framework.infra.di_container import singleton, DIContainer
from pepper.framework.infra.event.api import EventBusContainer
from pepper.framework.infra.event.memory import SynchronousEventBusContainer
from pepper.framework.infra.resource.threaded import ThreadedResourceContainer
from test import util


class TestBackendContainer(BackendContainer, EventBusContainer):
    @property
    @singleton
    def backend(self):
        # type: () -> TestBackend
        return TestBackend(self.event_bus, self.resource_manager)


class TestLed(AbstractLed):
    def __init__(self, event_bus, resource_manager):
        super(TestLed, self).__init__(event_bus, resource_manager)
        self.active = set()

    def set(self, leds, rgb, duration):
        self.active |= set(leds)

    def off(self, leds):
        self.active -= set(leds)


class TestBackend(AbstractBackend):
    def __init__(self, event_bus, resource_manager):
        super(TestBackend, self).__init__(led=TestLed(event_bus, resource_manager),
                                          camera=None, microphone=None, text_to_speech=None, motion=None, tablet=None)


class ApplicationContainer(TestBackendContainer, SynchronousEventBusContainer, ThreadedResourceContainer):
    def __init__(self):
        super(ApplicationContainer, self).__init__()


class TestIntention(ApplicationContainer, AbstractIntention, LedComponent):
    def __init__(self):
        super(TestIntention, self).__init__()


class TestApplication(AbstractApplication, ApplicationContainer):
    def __init__(self, intention):
        super(TestApplication, self).__init__(intention)


class LedITest(unittest.TestCase):
    def setUp(self):
        self.intention = TestIntention()
        self.application = TestApplication(self.intention)
        self.application.start()

    def tearDown(self):
        self.application.stop()
        del self.application
        DIContainer._singletons.clear()

    def test_activate(self):
        self.intention.activate_led([Led.LeftEarLed1, Led.RightEarLed2], (1, 2, 3), 4)

        util.await(lambda: len(self.intention.backend.led.active) > 1, msg="point event")

        active = self.intention.backend.led.active
        self.assertEqual(2, len(active))
        np.testing.assert_array_equal([Led.LeftEarLed1, Led.RightEarLed2], tuple(active))

        try:
            util.await(lambda: len(self.intention.backend.led.active) > 1, max=5)
        except unittest.TestCase.failureException:
            # Expect no more audio events
            pass

    def test_deactivate(self):
        self.intention.activate_led([Led.LeftEarLed1, Led.RightEarLed2], (1, 2, 3), 4)
        util.await(lambda: len(self.intention.backend.led.active) > 1, msg="point event")

        self.intention.deactivate_led([Led.LeftEarLed1])
        util.await(lambda: len(self.intention.backend.led.active) < 2, msg="point event")

        active = self.intention.backend.led.active
        self.assertEqual(1, len(active))
        self.assertEqual(Led.RightEarLed2, next(iter(active)))


if __name__ == '__main__':
    unittest.main()