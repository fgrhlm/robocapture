import sys
import cv2 as cv
import numpy as np
import queue
import json

from capture import RCVideoCapture
from ultralytics import YOLO
from ultralytics.engine.results import Results
from result import RCYoloResults
from utils.logger import logger, LogLevel

# https://docs.opencv.org/4.x/d0/dd4/tutorial_dnn_face.html
# https://docs.ultralytics.com/modes/predict/
# https://www.geeksforgeeks.org/object-detection-with-yolo-and-opencv/
# https://github.com/ultralytics/ultralytics/blob/main/docs/en/usage/simple-utilities.md
# https://docs.ultralytics.com/modes/predict/#inference-arguments

class RCYolo:
    """Thin wrapper around ultralytics YOLO model."""
    def __init__(self, yolo_path, config):
        self.path: str = yolo_path
        """Path to the yolo model"""
        self.config = config["yolo"]
        """YOLO model object"""
        self.model: YOLO = YOLO(yolo_path, task="detect", verbose=self.config["verbose"])
        
        if self.config["cpu"]:
            self.model = self.model.to("cpu")

    def detect(self, frame) -> RCYoloResults:
        """Runs inference on **`frame`** and returns the results"""
        frame_resize = cv.resize(frame, (640, 640))
        results: Results = self.model(
            frame_resize,
            verbose=self.config["verbose"],
            stream=self.config["stream"],
            conf=self.config["min_conf"],
            half=self.config["fp16"],
            max_det=self.config["max_detect"],
            vid_stride=self.config["vid_stride"]
        )

        results: RCYoloResults = RCYoloResults(results, self.model.names)

        return results

