import logging

class RCWorker:
    def __init__(self, name, config, queue, on_data=None, on_save=None):
        self.name = name
        self.config = config
        self.queue = queue
        self.stop_signal = False
        self.on_data = on_data
        self.on_save = on_save

    def stop(self):
        self.stop_signal = True
