import base64
import json
from io import BytesIO

from PIL import Image
from typing import List, Optional

from pepper.framework.backend.abstract.camera import TOPIC as CAM_TOPIC, AbstractImage
from pepper.framework.context.api import Context
from pepper.framework.event.api import Event, EventBus
from pepper.framework.monitoring.scene import Scene
from pepper.framework.monitoring.server.server import MonitoringServer
from pepper.framework.multiprocessing import TopicWorker, RejectionStrategy
from pepper.framework.sensor.api import FaceDetector, ObjectDetector
from pepper.framework.sensor.obj import Object

TOPIC = "pepper.framework.monitoring.topic"
TOPICS = (CAM_TOPIC, FaceDetector.TOPIC_KNOWN, ObjectDetector.TOPIC)


class MonitoringWorker(TopicWorker):
    """
    Display Robot Camera and Scene View in Browser
    """

    def __init__(self, context, server, name, event_bus, resource_manager):
        # type: (Context, MonitoringServer, str, EventBus, ResourceManager) -> None
        super(MonitoringWorker, self).__init__(TOPICS, event_bus, interval=0, name=name,
                                               buffer_size=16, rejection_strategy=RejectionStrategy.DROP,
                                               resource_manager=resource_manager,
                                               requires=TOPICS, provides=[TOPIC])
        self._context = context
        self._server = server
        self._display_info = {}
        self._scene = Scene()

    def process(self, event):
        # type: (Optional[Event]) -> None
        if CAM_TOPIC == event.metadata.topic:
            self.on_image(event.payload)
        elif ObjectDetector.TOPIC == event.metadata.topic or FaceDetector.TOPIC == event.metadata.topic:
            self.add_items(event.payload)
        else:
            raise ValueError("Unknown topic: " + event.metadata.topic)

    def on_image(self, image):
        # type: (AbstractImage) -> None
        """
        Private On Image Event

        Parameters
        ----------
        image: Image
        """
        # Get Scatter Coordinates

        # Update Server with Display Info of previous image with added items
        self.event_bus.publish(TOPIC, Event(json.dumps(self. _display_info), None))

        self._scene.on_image(image)
        x, y, z, c = self._scene.scatter_map

        # Construct Display Info (to be send to webclient)
        self._display_info = {
            "hash": hash(str(image.image)),
            "img": self.encode_image(Image.fromarray(image.image)),
            "frustum": image.frustum(.5, 4),
            "items": [],
            "items3D": [{
                "position": item.position,
                "bounds3D": item.bounds3D
            } for item in self._context.objects],

            "x": x.tolist(),
            "y": y.tolist(),
            "z": z.tolist(),
            "c": c.tolist()
        }

    def encode_image(self, image):
        # type: (Image) -> str
        """
        Encode PIL Image as base64 PNG

        Parameters
        ----------
        image: Image
        Returns
        -------
        base64: str
            Base64 encoded PNG string
        """

        with BytesIO() as png:
            image.save(png, 'png')
            png.seek(0)
            return base64.b64encode(png.read())

    def add_items(self, items):
        # type: (List[Object]) -> None
        """
        Add Items (Objects + Faces) to Display

        Parameters
        ----------
        items: List[Object]
        """
        if self._display_info:  # If Ready to Populate
            # Add Items to Display Info
            self._display_info["items"] += [
                {"name": item.name,
                 "confidence": item.confidence,
                 "bounds": item.image_bounds.to_list(),
                 "position": item.position,
                 "bounds3D": item.bounds3D,
                 } for item in items]
