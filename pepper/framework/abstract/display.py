from pepper.framework.abstract.component import AbstractComponent
from pepper.framework.backend.abstract.tablet import TOPIC
from pepper.framework.event.api import Event


class DisplayComponent(AbstractComponent):
    """
    Show content on the robot's display.
    """

    def __init__(self):
        super(DisplayComponent, self).__init__()

        self._log.info("Initializing DisplayComponent")

    def show_on_display(self, url):
        # type: (Union[str, unicode]) -> None
        """
        Show URL

        Parameters
        ----------
        url: str
            WebPage/Image URL
        """
        event = Event({'url': url}, None)
        self.event_bus.publish(TOPIC, event)

    def hide_display(self):
        # type: () -> None
        """Hide whatever is shown on the display"""
        event = Event({'url': None}, None)
        self.event_bus.publish(TOPIC, event)

