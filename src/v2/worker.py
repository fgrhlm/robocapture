import logging

from pipeline import RCPipeline

class RCWorker:
    def __init__(self, config, stop_event, data_queue):
        self.stop_event = stop_event
        self.queue = data_queue
        self.config = config
   
        try:
            self.pipeline = RCPipeline(self.config)
        except Exception as e:
            logging.error(f"Could not load pipeline!")
            self.stop_event.set()
