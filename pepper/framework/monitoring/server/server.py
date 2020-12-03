import logging
import os
import sys
import webbrowser

import tornado.ioloop
import tornado.template
import tornado.web
import tornado.websocket

logger = logging.getLogger(__name__)


if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class MonitoringServer(tornado.web.Application):
    """Display Server for :class:`~pepper.framework.component.display.display.DisplayComponent`"""

    ROOT = os.path.join(os.path.dirname(__file__), "web")
    PORT = 9090
    HANDLERS = set()

    def __init__(self):
        # Host web/index.html
        self.event_loop = None

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
        tornado.ioloop.IOLoop().make_current()
        self.event_loop = tornado.ioloop.IOLoop.current()

        self.listen(self.PORT)
        webbrowser.open("http://localhost:{}".format(self.PORT))

        logger.debug("Starting tornado server on %s", self.PORT)
        tornado.ioloop.IOLoop.current().start()
        logger.debug("Stopped tornado server on %s", self.PORT)

    def stop(self):
        tornado.ioloop.IOLoop.instance().stop()
        logger.debug("Stopped tornado server")

    def update(self, json):
        # type: (str) -> None
        """Update WebServer"""
        if self.event_loop and json:
            for handler in self.HANDLERS:
                self.event_loop.add_callback(lambda: handler.write_message(json))
