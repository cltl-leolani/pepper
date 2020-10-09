import logging
import socket

import numpy as np

from pepper.framework.infra.util import Bounds
from .api import FaceDetector

logger = logging.getLogger(__name__)


class OpenFace(FaceDetector):
    """
    Perform Face Recognition Using OpenFace

    This requires a Docker Image of ```bamos/openface``` and Docker Running, see `The Installation Guide <https://github.com/cltl/pepper/wiki/Installation#3-openface--docker>`_

    It will then connect a client to this server to request face representations via a socket connection.
    """

    HOST, PORT = '127.0.0.1', 8989

    def __init__(self):
        self._log = logger.getChild(self.__class__.__name__)

    def represent(self, image):
        """
        Represent Face in Image as 128-dimensional vector

        Parameters
        ----------
        image: np.ndarray
            Image (possibly containing a human face)

        Returns
        -------
        result: list of (np.ndarray, Bounds)
            List of (representation, bounds)
        """

        try:
            # Connect to OpenFace Service
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.HOST, self.PORT))

            # Send Image
            client.send(np.array(image.shape, np.int32))
            client.sendall(image.tobytes())

            # Receive Number of Faces in Image
            n_faces = np.frombuffer(client.recv(4), np.int32)
            if not len(n_faces):
                raise RuntimeError("Connection terminated unexpectedly")

            # Wrap information into Face instances
            faces = []
            for i in range(n_faces[0]):

                # Face Bounds
                bounds = Bounds(*np.frombuffer(client.recv(4*4), np.float32))
                bounds = bounds.scaled(1.0 / image.shape[1], 1.0 / image.shape[0])

                # Face Representation
                representation = np.frombuffer(client.recv(self.FEATURE_DIM * 4), np.float32)

                faces.append((representation, bounds))

            return faces

        except socket.error:
            raise RuntimeError("Couldn't connect to OpenFace Docker service.")

    def stop(self):
        super(OpenFace, self).stop()
