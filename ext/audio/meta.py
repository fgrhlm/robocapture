import whisper
import logging
import numpy as np

from src.ext import RCExtWorker

class RCAudioMeta(RCExtWorker):
    def __init__(self, config: dict):
        RCExtWorker.__init__(self, "meta_audio", config)

    def process(self, data):
        level = np.linalg.norm(data)

        return {
            "name": self.name,
            "data": {
                "level": float(level)
            }
        }

ext = RCAudioMeta
