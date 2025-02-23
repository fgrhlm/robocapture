import sys
import cv2 as cv
import numpy as np

from cv2.dnn import DNN_BACKEND_CUDA,DNN_BACKEND_OPENCV,DNN_TARGET_CPU,DNN_TARGET_CUDA
from capture import RCVideoCapture
from result import RCYunetResults
from utils.logger import logger

# https://docs.opencv.org/4.x/df/d20/classcv_1_1FaceDetectorYN.html
# https://opencv.org/blog/opencv-face-detection-cascade-classifier-vs-yunet/

class RCYunet:
    def __init__(self, yunet_path, config):
        self.config = config["yunet"]
        self.config["img_size"] = [int(n/2) for n in self.config["img_size"]]

        self.path = yunet_path

        backend = DNN_BACKEND_OPENCV if self.config["cpu"] else DNN_BACKEND_OPENCV
        target = DNN_TARGET_CPU if self.config["cpu"] else DNN_TARGET_CUDA

        self.model = cv.FaceDetectorYN.create(
            yunet_path,
            "",
            self.config["img_size"],
            self.config["min_detect"],
            self.config["max_nms"],
            self.config["top_k"],
            backend_id=backend,
            target_id=target
        )

        self.model.setInputSize(self.config["img_size"])

    def detect(self, frame) -> RCYunetResults:
        frame_half = cv.resize(frame, self.config["img_size"])
        results: list[int, list] = self.model.detect(frame_half)
        results: RCYunetResults = RCYunetResults(results)

        return results
       
