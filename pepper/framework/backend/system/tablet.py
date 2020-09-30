from pepper.framework.backend.abstract.tablet import AbstractTablet


class SystemTablet(AbstractTablet):
    """Access Robot Tablet to show URLs"""

    def __init__(self, event_bus):
        # type: (EventBus) -> None
        super(SystemTablet, self).__init__(event_bus)

    def show(self, url):
        # type: (str) -> None
        """
        Show URL

        Parameters
        ----------
        url: str
            WebPage/Image URL
        """
        self._log.info("Show URL: " + str(url)[:80])

    def hide(self):
        # type: () -> None
        """Hide whatever is shown on tablet"""
        self._log.info("Hide display")
