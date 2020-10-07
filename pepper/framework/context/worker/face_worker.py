from pepper.framework.event.api import Event
from pepper.framework.multiprocessing import TopicWorker, RejectionStrategy
from pepper.framework.sensor.api import FaceDetector


class ContextFaceWorker(TopicWorker):
    def __init__(self, context, name, event_bus, resource_manager):
        # type: (Context, str, EventBus, ResourceManager) -> None
        super(ContextFaceWorker, self).__init__(FaceDetector.TOPIC, event_bus, interval=0, name=name,
                                                buffer_size=16, rejection_strategy=RejectionStrategy.BLOCK,
                                                resource_manager=resource_manager,
                                                requires=[FaceDetector.TOPIC], provides=[])
        self.context = context

    def process(self, event):
        # type: (Event) -> None
        people = event.payload

        self.context.add_people(people)
