import logging

class RCYolo:
    def __init__(self, config):
        self.name = "yolo"
        self.config = config
        logging.debug("YOLO!")

    def process(self, data):
        pass

pipeline_step = RCYolo
