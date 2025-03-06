import logging
from threading import Thread

class RCThread(Thread):
    def __init__(self, name, config, stop_event, data_queue):
        Thread.__init__(self)
        self.name = name
        self.ready = False
        self.config = config
        self.stop_event = stop_event
        self.queue = data_queue

    def set_ready(self, ready):
        self.ready = ready

    def is_ready(self):
        return self.ready

    def run(self):
        logging.error("Thread target function is empty!")
        self.stop_event.set()

