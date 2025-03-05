import logging

from threading import Thread
from pipeline import RCPipeline

# https://numpy.org/doc/stable/reference/generated/numpy.fft.fft.html
# https://stackoverflow.com/questions/4315989/python-frequency-analysis-of-sound-files

class RCAudio:
    def __init__(self, pipeline, stop_event, data_queue):
        self.stop_event = stop_event
        self.queue = data_queue

    def run(self):
        logging.info("Starting RCAudio..")

        while True:
            if self.stop_event and self.stop_event.is_set():
                break

        logging.info("Stopping RCAudio..")

class RCAudioThread(Thread):
    def __init__(self, config, stop_event, data_queue):
        Thread.__init__(self)
        self.stop_event = stop_event
        self.queue = data_queue
        self.pipeline = RCPipeline(
            config.get("pipeline")
        )

    def run(self):
        audio = RCAudio(self.pipeline, self.stop_event, self.queue) 
        audio.run()
