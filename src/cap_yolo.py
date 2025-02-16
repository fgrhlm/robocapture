import sys
import cv2 as cv
import numpy as np
import queue

from capture import RCVideoCapture
from ultralytics import YOLO
from utils.logger import logger, LogLevel

# https://docs.opencv.org/4.x/d0/dd4/tutorial_dnn_face.html
# https://docs.ultralytics.com/modes/predict/
# https://www.geeksforgeeks.org/object-detection-with-yolo-and-opencv/
# https://docs.python.org/3/library/queue.html#queue.SimpleQueue

class YOLOCapture:
    def __init__(self, yolo_path, source):
        self.path = yolo_path
        self.cap = RCVideoCapture(source)
        self.model = YOLO(yolo_path)

    def detect(self, frame, _queue=None):
        results = self.model(frame, verbose = False)
        results_json = results[0].to_json()

        if _queue:
            try:
                if len(results_json) > 0:
                    _queue.put(results_json)
            except queue.Full:
                logger("YOLOCapture", "Queue is full!", level=LogLevel.WARNING)
   
    def run(self,_queue=None):
        logger("YOLOCapture", "Running..")

        self.cap.process(self.detect, _queue=_queue)
        cv.destroyAllWindows()

        logger("YOLOCapture", "Goodbye!")
