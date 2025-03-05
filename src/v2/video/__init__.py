import logging

from threading import Thread
from pipeline import RCPipeline

class RCVideo:
    def __init__(self, config):
        pass
    
    def run(self, stop_event=stop_event):
        logging.info("Starting RCVideo..")

        while True:
            if stop_event and stop_event.is_set():
                break

        logging.info("Stopping RCVideo..")

class RCVideoThread(Thread):
    def __init__(self, config, stop_event = None):
        Thread.__init__(self)
        self.stop_event = stop_event
        self.pipeline = RCPipeline(
            config.get("pipeline")
        )

    def run(self):
        video = RCVideo(self.pipeline, stop_event=self.stop_event) 
        video.run()
