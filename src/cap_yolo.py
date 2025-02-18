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

class RCYolo:
    def __init__(self, yolo_path):
        self.path = yolo_path
        self.model = YOLO(yolo_path)

    def detect(self, frame):
        results = self.model(frame, verbose = False)

        r = []
        for n in results:
            classes = n.boxes.cls.cpu().numpy()
            confs = n.boxes.conf.cpu().numpy()
            boxes = n.boxes.xyxy.cpu().numpy()

            for _class, _conf, _box in zip(classes, confs, boxes):
                r.append({
                    self.model.names[int(_class)]: float(_conf)
                })
        
        return r 
