import logging

from threading import Thread
from pipeline import RCPipeline

# https://numpy.org/doc/stable/reference/generated/numpy.fft.fft.html
# https://stackoverflow.com/questions/4315989/python-frequency-analysis-of-sound-files

class RCAudio:
    def __init__(self, pipeline):
        pass

    def run(self):
        logging.info("Starting RCAudio..")

        while True:
            if stop_event and stop_event.is_set():
                break

        logging.info("Stopping RCAudio..")

class RCAudioThread(Thread):
    def __init__(self, config, stop_event=None):
        Thread.__init__(self)
        self.stop_event = stop_event
        self.pipeline = RCPipeline(
            config.get("pipeline")
        )

    def run(self):
        audio = RCAudio(self.pipeline, stop_event=self.stop_event) 
        audio.run()
