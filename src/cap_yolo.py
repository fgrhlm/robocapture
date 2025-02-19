import sys
import cv2 as cv
import numpy as np
import queue

from capture import RCVideoCapture
from ultralytics import YOLO
from ultralytics.engine.results import Results
from result import RCYoloResults
from utils.logger import logger, LogLevel

# https://docs.opencv.org/4.x/d0/dd4/tutorial_dnn_face.html
# https://docs.ultralytics.com/modes/predict/
# https://www.geeksforgeeks.org/object-detection-with-yolo-and-opencv/
# https://github.com/ultralytics/ultralytics/blob/main/docs/en/usage/simple-utilities.md

class RCYolo:
    """Thin wrapper around ultralytics YOLO model."""
    def __init__(self, yolo_path):
        self.path: str = yolo_path
        """Path to the yolo model"""
        self.model: YOLO = YOLO(yolo_path)
        """YOLO model object"""

    def detect(self, frame) -> RCYoloResults:
        """Runs inference on **`frame`** and returns the results"""
        results: Results = self.model(frame, verbose = False)
        results: RCYoloResults = RCYoloResults(results, self.model.names)

        return results

