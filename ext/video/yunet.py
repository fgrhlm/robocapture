import logging
import sys
import cv2 as cv
import numpy as np

from cv2.dnn import DNN_BACKEND_CUDA,DNN_BACKEND_OPENCV,DNN_TARGET_CPU,DNN_TARGET_CUDA

from src.ext import RCExtWorker

# https://docs.opencv.org/4.x/df/d20/classcv_1_1FaceDetectorYN.html
# https://opencv.org/blog/opencv-face-detection-cascade-classifier-vs-yunet/

class RCYunet:
    def __init__(self, config):
        RCExtWorker.__init__(self, "yunet", config)
        self.config["img_size"] = [int(n/2) for n in self.config["img_size"]]

        self.yunet = cv.FaceDetectorYN.create(
            self.config["weights"],
            "",
            self.config["img_size"],
            self.config["min_detect"],
            self.config["max_nms"],
            self.config["top_k"],
            backend_id=DNN_BACKEND_OPENCV if self.config["cpu"] else DNN_BACKEND_OPENCV,
            target_id=DNN_TARGET_CPU if self.config["cpu"] else DNN_TARGET_CUDA
        )

        self.yunet.setInputSize(self.config["img_size"])

    def process(self, frame):
        f = cv.resize(frame, self.config["img_size"])
        results = []

        for n in self.yunet.detect(f)[1]:
            conf = float(n[-1])
            box_x = int(n[0])
            box_y = int(n[1])
            box_w = box_x + int(n[2])
            box_h = box_y + int(n[3])

            results.append({
                "class": "face",
                "conf": conf,
                "box": {"x": box_x,"y": box_y,"w": box_w,"h": box_h}
            })

        return {
            "name": "yunet",
            "data": results
        }

ext = RCYunet
