import logging
import sys
import cv2 as cv
import numpy as np
import queue
import json

from pipeline import RCPipelineResult
from ultralytics import YOLO
from ultralytics.engine.results import Results

# https://docs.opencv.org/4.x/d0/dd4/tutorial_dnn_face.html
# https://docs.ultralytics.com/modes/predict/
# https://www.geeksforgeeks.org/object-detection-with-yolo-and-opencv/
# https://github.com/ultralytics/ultralytics/blob/main/docs/en/usage/simple-utilities.md
# https://docs.ultralytics.com/modes/predict/#inference-arguments

class RCYolo:
    def __init__(self, config):
        self.name = "yolo"
        self.config = config["ext"]["yolo"]

        self.yolo = YOLO(
            self.config["checkpoint"],
            task="detect",
            verbose=self.config["verbose"]
        )

        if self.config["cpu"]:
            self.yolo = self.yolo.to("cpu")

    def process(self, frame):
        f = cv.resize(frame, (640, 640)) 

        results = self.yolo(
            f,
            verbose=self.config["verbose"],
            stream=self.config["stream"],
            conf=self.config["min_conf"],
            half=self.config["fp16"],
            max_det=self.config["max_detect"],
            vid_stride=self.config["vid_stride"]
        )
       
        results = RCPipelineResult("yolo", results)
        
        return results

step = RCYolo
