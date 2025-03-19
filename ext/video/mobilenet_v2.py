import os
import logging
import sys
import cv2 as cv
import numpy as np
import queue
import json
import enum

from keras.api.applications import MobileNetV2
from keras.api.applications.imagenet_utils import decode_predictions
from keras.api.applications.mobilenet_v2 import preprocess_input
from dataclasses import dataclass

from src.ext import RCExtWorker

class RCMobilenetV2(RCExtWorker):
    def __init__(self, config):
        RCExtWorker.__init__(self, "mobilenet", config)
        self.model = MobileNetV2()

    def process(self, frame):
        img = cv.resize(frame, (self.config["img_size"][0], self.config["img_size"][1]))
        img = np.expand_dims(img,axis=0)
        img = preprocess_input(img)
        pred = self.model.predict(img)
        results = decode_predictions(pred)

        return {
            "name": "mobilenet",
            "data": results
        }

ext = RCMobilenetV2
