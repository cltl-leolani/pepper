import unittest

import numpy as np

from pepper.framework.abstract.application import AbstractApplication
from pepper.framework.abstract.display import DisplayComponent
from pepper.framework.abstract.led import LedComponent
from pepper.framework.backend.abstract.backend import AbstractBackend
from pepper.framework.backend.abstract.led import AbstractLed, Led
from pepper.framework.backend.abstract.tablet import AbstractTablet
from pepper.framework.backend.container import BackendContainer
from pepper.framework.di_container import singleton
from pepper.framework.event.api import EventBusContainer
from pepper.framework.event.memory import SynchronousEventBusContainer
from pepper.framework.resource.threaded import ThreadedResourceContainer
from test import util


class TestBackendContainer(BackendContainer, EventBusContainer):
    @property
    @singleton
    def backend(self):
        # type: () -> TestBackend
        return TestBackend(self.event_bus, self.resource_manager)


class TestTablet(AbstractTablet):
    def __init__(self, event_bus):
        super(TestTablet, self).__init__(event_bus)
        self.display = None

    def show(self, url):
        self.display = url

    def hide(self):
        self.display = None


class TestBackend(AbstractBackend):
    def __init__(self, event_bus, resource_manager):
        super(TestBackend, self).__init__(tablet=TestTablet(event_bus),
                                          camera=None, microphone=None, text_to_speech=None, motion=None, led=None)


class ApplicationContainer(TestBackendContainer, SynchronousEventBusContainer, ThreadedResourceContainer):
    def __init__(self):
        super(ApplicationContainer, self).__init__()


class TestApplication(ApplicationContainer, AbstractApplication, DisplayComponent):
    def __init__(self):
        super(TestApplication, self).__init__()


class DisplayITest(unittest.TestCase):
    def setUp(self):
        self.application = TestApplication()
        self.application.start()

    def tearDown(self):
        self.application.stop()
        del self.application

    def test_show(self):
        self.application.show_on_display("test://url")

        util.await(lambda: self.application.backend.tablet.display, msg="point event")

        self.assertEqual("test://url", self.application.backend.tablet.display)


    def test_hide(self):
        self.application.show_on_display("test://url")
        util.await(lambda: self.application.backend.tablet.display, msg="point event")

        self.application.hide_display()
        util.await(lambda: not self.application.backend.tablet.display, msg="point event")

        self.assertIsNone(self.application.backend.tablet.display)


if __name__ == '__main__':
    unittest.main()