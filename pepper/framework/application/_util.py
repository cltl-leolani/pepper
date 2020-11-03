def event_payload_handler(handler):
    def wrapped(self, event):
        handler(self, event.payload)

    return wrapped