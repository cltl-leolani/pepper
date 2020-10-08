from typing import Union

from pepper.framework.event.api import EventBus
from pepper.framework.resource.api import ResourceManager

TOPIC = "pepper.framework.backend.abstract.tablet.topic"


class AbstractTablet(object):
    """Access Robot Tablet to show URLs"""

    def __init__(self, event_bus, resource_manager):
        # type: (EventBus, ResourceManager) -> None
        event_bus.subscribe(TOPIC, self._event_handler)
        resource_manager.provide_resource(TOPIC)

    def _event_handler(self, event):
        payload = event.payload
        url = payload['url']

        if url:
            self.show(url)
        else:
            self.hide()

    def show(self, url):
        # type: (Union[str, unicode]) -> None
        """
        Show URL

        Parameters
        ----------
        url: str
            WebPage/Image URL
        """
        raise NotImplementedError()

    def hide(self):
        # type: () -> None
        """Hide whatever is shown on tablet"""
        raise NotImplementedError()
