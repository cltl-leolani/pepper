import time
import uuid

from pepper.framework.di_container import DIContainer


class TopicError(ValueError):
    pass


class EventBusContainer(DIContainer):
    @property
    def event_bus(self):
        # type: () -> EventBus
        raise ValueError("No EventBus configured")


class EventBus(object):
    """
    Supports publishing of and subscribing to events based on topics.

    Events published to a topic are delivered to all subscribers in the order
    of their arrival. Publishing and invocation of the subscribed handler
    can be asynchronous. Subscribers receive only events that arrive after they
    subscribed to a topic.
    """

    def publish(self, topic, event):
        raise NotImplementedError()

    def subscribe(self, topic, handler):
        raise NotImplementedError()

    def unsubscribe(self, topic, handler=None):
        raise NotImplementedError()

    @property
    def topics(self):
        raise NotImplementedError()

    @property
    def has_topic(self, topic):
        return topic in self.topics


class Event(object):
    def __init__(self, payload, metadata=None, id=None):
        self._id = id if id else str(uuid.uuid4())
        self._payload = payload
        self._metadata = metadata if metadata else EventMetadata(timestamp=time.time())

    def with_topic(self, topic):
        # type: (str) -> Event
        return Event(self._payload, self._metadata.with_(topic=topic), id=self._id)

    @property
    def metadata(self):
        # type: () -> EventMetadata
        return self._metadata

    @property
    def payload(self):
        # type: () -> object
        return self._payload

    def __eq__(self, other):
        return self._id == other._id


class EventMetadata(object):
    def __init__(self, timestamp=None, offset=None, topic=None):
        # type: (int, int, str) -> None
        self._timestamp = timestamp
        self._offset = offset
        self._topic = topic

    def with_(self, timestamp=None, offset=None, topic=None):
        # type: (int, str) -> None
        new_timestamp = offset if offset is not None else self._timestamp
        new_offset = offset if offset is not None else self._offset
        new_topic = topic if topic is not None else self._topic
        return EventMetadata(new_timestamp, new_offset, new_topic)

    @property
    def topic(self):
        # type: () -> str
        return self._topic

    @property
    def timestamp(self):
        # type: () -> int
        return self._timestamp

    @property
    def offset(self):
        # type: () -> int
        return self._offset
