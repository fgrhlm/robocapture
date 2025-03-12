import logging
import sys
import cv2 as cv
import numpy as np

from base64 import b64encode

class RCFrameB64:
    def __init__(self, config):
        self.name = "frameb64"

    def process(self, frame):
        return {
            "name": "frame",
            "data": b64encode(cv.imencode(".jpg", frame)[1]).decode()
        }

ext = RCFrameB64
