import logging

import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template

import webbrowser

import os


logger = logging.getLogger(__name__)


class MonitoringServer(tornado.web.Application):
    """Display Server for :class:`~pepper.framework.component.display.display.DisplayComponent`"""

    ROOT = os.path.join(os.path.dirname(__file__), "web")
    PORT = 9090
    HANDLERS = set()

    def __init__(self):
        # Host web/index.html
        class BaseHandler(tornado.web.RequestHandler):
            def get(self):
                loader = tornado.template.Loader(MonitoringServer.ROOT)
                self.write(loader.load("index.html").generate())

        # Accept Web Socket Connections
        class WSHandler(tornado.websocket.WebSocketHandler):
            def __init__(self, application, request, **kwargs):
                super(WSHandler, self).__init__(application, request, **kwargs)

            def open(self):
                MonitoringServer.HANDLERS.add(self)

            def on_close(self):
                MonitoringServer.HANDLERS.remove(self)

        super(MonitoringServer, self).__init__([(r'/ws', WSHandler), (r'/', BaseHandler)])

    def start(self):
        # type: () -> None
        """Start WebServer"""
        self.listen(self.PORT)
        webbrowser.open("http://localhost:{}".format(self.PORT))
        logger.debug("Starting tornado server on %s", self.PORT)
        tornado.ioloop.IOLoop.instance().start()
        logger.debug("Stopped tornado server on %s", self.PORT)

    def stop(self):
        tornado.ioloop.IOLoop.instance().stop()
        logger.debug("Stopped tornado server")

    def update(self, json):
        # type: (str) -> None
        """Update WebServer"""
        if json:
            for handler in self.HANDLERS:
                handler.write_message(json)
