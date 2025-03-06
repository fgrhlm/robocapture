import logging

class RCYunet:
    def __init__(self, config):
        self.name = "yunet"
        self.config = config
        logging.debug("Yunet!")

    def process(self, data):
        pass

step = RCYunet
