import whisper
import logging
import numpy as np

class RCAudioMeta:
    def __init__(self, config: dict):
        self.name = "audio-meta"
        self.config = config

    def process(self, data):
        level = np.linalg.norm(data)

        return {
            "name": "meta",
            "data": {
                "level": float(level)
            }
        }

ext = RCAudioMeta
