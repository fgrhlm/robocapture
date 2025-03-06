import logging

from threads import RCThread
from pipeline import RCPipeline

class RCVideo:
    def __init__(self, config, stop_event, data_queue):
        self.stop_event = stop_event
        self.queue = data_queue
        self.config = config
        
        self.pipeline = RCPipeline(self.config)

    def run(self):
        logging.info("Starting RCVideo..")

        while True:
            if self.stop_event and self.stop_event.is_set():
                break

        logging.info("Stopping RCVideo..")

class RCVideoThread(RCThread):
    def __init__(self, config, stop_event, data_queue):
        Thread.__init__(self, "t_video", config, stop_event, data_queue)

    def run(self):
        video = RCVideo(self.config, self.stop_event, self.queue) 
        
        self.set_ready(True)
        video.run()
