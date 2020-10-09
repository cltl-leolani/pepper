import logging

from typing import Iterator, ClassVar

from pepper.framework.application.application import AbstractApplication
from pepper.framework.application.component import AbstractComponent
from pepper.framework.application.component import ComponentDependencyError

logger = logging.getLogger(__name__)


class AbstractIntention(object):
    """
    The Intention class is at the base of more involved robot applications.
    They build on top of :class:`~pepper.framework.application.application.AbstractApplication`
    instances and allow for switching between robot behaviours.

    Parameters
    ----------
    application: AbstractApplication
        :class:`~pepper.framework.application.application.AbstractApplication` to base Intention on
    """

    def __init__(self, application):
        # type: (AbstractApplication) -> None
        self._application = application

        # Reset Application Events to their default
        # This prevents events from previous Intention to still be called!
        self.application._reset_events()

        # Subscribe to all Application Events, while making sure all Dependencies are met.
        for dependency in self.dependencies:
            self.require_dependency(dependency)

        # Subscribe to all Application Members, essentially becoming the Application
        self.__dict__.update({k: v for k, v in self.application.__dict__.items() if k not in self.__dict__})

        # Update User of Intention Switch
        self._log = logger.getChild(self.__class__.__name__)
        self.log.info("<- Switched Intention")

    @property
    def log(self):
        """
        Intention `Logger <https://docs.python.org/2/library/logging.html>`_

        Returns
        -------
        log: logging.Logger
        """
        return self._log

    @property
    def application(self):
        # type: () -> AbstractApplication
        """
        The :class:`~pepper.framework.application.application.AbstractApplication` Intention is based on

        Returns
        -------
        application: AbstractApplication
        """
        return self._application

    @property
    def dependencies(self):
        # type: () -> Iterator[ClassVar[AbstractComponent]]
        """
        Intention Dependencies

        Yields
        ------
        components: iterable of AbstractComponent
        """

        # Go Through Method Resolution Order, finding all strict subclasses of AbstractComponent,
        #   excluding AbstractApplication or AbstractIntention.
        # These are the components that the user requested and must be linked to this Intention
        for cls in self.__class__.mro():
            if issubclass(cls, AbstractComponent) and not cls == AbstractComponent and \
                    not issubclass(cls, AbstractApplication) and not issubclass(cls, AbstractIntention):
                yield cls

    def require_dependency(self, dependency):
        # type: (ClassVar[AbstractComponent]) -> AbstractComponent
        """
        Enforce Component Dependency

        Checks whether Component is included in :class:`~pepper.framework.application.application.AbstractApplication`

        Parameters
        ----------
        dependency: type
            Required Component Type

        Returns
        -------
        dependency: AbstractComponent
            Requested Dependency (which is ensured to be included in this application, when no exception is thrown)
        """

        if not isinstance(self.application, dependency):
            raise ComponentDependencyError("{} depends on {}, which is not included in {}".format(
                self.__class__.__name__, dependency.__name__, self.application.__class__.__name__))

        for attribute in dir(dependency):
            if attribute.startswith(AbstractApplication._EVENT_TAG):
                self._application.__setattr__(attribute, self.__getattribute__(attribute))

        return self.application
