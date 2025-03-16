import logging
import sys
import cv2 as cv
import numpy as np

from base64 import b64encode
from src.ext import RCExtWorker

class RCFrameB64:
    def __init__(self, config):
        RCExtWorker.__init__(self, "frame", config)

    def process(self, frame):
        return {
            "name": self.name,
            "data": b64encode(cv.imencode(".jpg", frame)[1]).decode()
        }

ext = RCFrameB64
