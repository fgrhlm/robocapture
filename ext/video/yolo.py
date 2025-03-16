import logging
import sys
import cv2 as cv
import numpy as np
import queue
import json

from ultralytics import YOLO
from ultralytics.engine.results import Results

from src.ext import RCExtWorker

# https://docs.opencv.org/4.x/d0/dd4/tutorial_dnn_face.html
# https://docs.ultralytics.com/modes/predict/
# https://www.geeksforgeeks.org/object-detection-with-yolo-and-opencv/
# https://github.com/ultralytics/ultralytics/blob/main/docs/en/usage/simple-utilities.md
# https://docs.ultralytics.com/modes/predict/#inference-arguments

class RCYolo(RCExtWorker):
    def __init__(self, config):
        RCExtWorker.__init__(self, "yolo", config)

        self.yolo = YOLO(
            self.config["weights"],
            verbose=self.config["verbose"]
        )

        if self.config["cpu"]:
            self.yolo = self.yolo.to("cpu")

    def process(self, frame):
        f = cv.resize(frame, (self.config["img_size"][0],self.config["img_size"][1]))

        raw_results: Results = self.yolo(
            f,
            verbose=self.config["verbose"],
            stream=self.config["stream"],
            conf=self.config["min_conf"],
            half=self.config["fp16"],
            max_det=self.config["max_detect"],
            vid_stride=self.config["vid_stride"]
        )

        results = []
        for n in raw_results:
            classes = [int(x) for x in n.boxes.cls.cpu().numpy()]
            confs = [float(x) for x in n.boxes.conf.cpu().numpy()]
            boxes = n.boxes.xywh.cpu().numpy()

            for _class, _conf, _box in zip(classes, confs, boxes):
                results.append({
                    "class": self.yolo.names[_class],
                    "conf": _conf,
                    "box": {
                        "x": int(_box[0]),
                        "y": int(_box[1]),
                        "w": int(_box[2]),
                        "h": int(_box[3])
                    }
                })

        return {
            "name": "yolo",
            "data": results
        }

ext = RCYolo
