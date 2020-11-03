import unittest

from pepper.framework.application.application import AbstractApplication
from pepper.framework.application.display import DisplayComponent
from pepper.framework.application.intention import AbstractIntention
from pepper.framework.backend.abstract.backend import AbstractBackend
from pepper.framework.backend.abstract.tablet import AbstractTablet
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


class TestTablet(AbstractTablet):
    def __init__(self, event_bus, resource_manager):
        super(TestTablet, self).__init__(event_bus, resource_manager)
        self.display = None

    def show(self, url):
        self.display = url

    def hide(self):
        self.display = None


class TestBackend(AbstractBackend):
    def __init__(self, event_bus, resource_manager):
        super(TestBackend, self).__init__(tablet=TestTablet(event_bus, resource_manager),
                                          camera=None, microphone=None, text_to_speech=None, motion=None, led=None)


class ApplicationContainer(TestBackendContainer, SynchronousEventBusContainer, ThreadedResourceContainer):
    def __init__(self):
        super(ApplicationContainer, self).__init__()


class TestIntention(ApplicationContainer, AbstractIntention, DisplayComponent):
    def __init__(self):
        super(TestIntention, self).__init__()


class TestApplication(AbstractApplication, ApplicationContainer):
    def __init__(self, intention):
        super(TestApplication, self).__init__(intention)


class DisplayITest(unittest.TestCase):
    def setUp(self):
        self.intention = TestIntention()
        self.appliation = TestApplication(self.intention)
        self.appliation.start()

    def tearDown(self):
        self.appliation.stop()
        del self.appliation
        DIContainer._singletons.clear()

    def test_show(self):
        self.intention.show_on_display("test://url")

        util.await(lambda: self.intention.backend.tablet.display, msg="point event")

        self.assertEqual("test://url", self.intention.backend.tablet.display)


    def test_hide(self):
        self.intention.show_on_display("test://url")
        util.await(lambda: self.intention.backend.tablet.display, msg="point event")

        self.intention.hide_display()
        util.await(lambda: not self.intention.backend.tablet.display, msg="point event")

        self.assertIsNone(self.intention.backend.tablet.display)


if __name__ == '__main__':
    unittest.main()