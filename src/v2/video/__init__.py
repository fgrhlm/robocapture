import logging

from threading import Thread
from pipeline import RCPipeline

class RCVideo:
    def __init__(self, config, stop_event, data_queue):
        self.stop_event = stop_event
        self.queue = data_queue

    def run(self):
        logging.info("Starting RCVideo..")

        while True:
            if self.stop_event and self.stop_event.is_set():
                break

        logging.info("Stopping RCVideo..")

class RCVideoThread(Thread):
    def __init__(self, config, stop_event, data_queue):
        Thread.__init__(self)
        self.stop_event = stop_event
        self.queue = data_queue
        self.pipeline = RCPipeline(
            config.get("pipeline")
        )

    def run(self):
        video = RCVideo(self.pipeline, self.stop_event, self.queue) 
        video.run()
