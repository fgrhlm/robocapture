import sys
import cv2 as cv
import numpy as np

from capture import RCVideoCapture
from result import RCYunetResults
from utils.logger import logger

# https://docs.opencv.org/4.x/df/d20/classcv_1_1FaceDetectorYN.html
# https://opencv.org/blog/opencv-face-detection-cascade-classifier-vs-yunet/

class RCYunet:
    def __init__(self, yunet_path, cap_size):
        self.path = yunet_path

        self.model = cv.FaceDetectorYN.create(
            yunet_path,
            "",
            (320,320),
            0.6,
            0.3,
            5000
        )

        self.model.setInputSize(cap_size)

    def detect(self, frame) -> RCYunetResults:
        results: list[int, list] = self.model.detect(frame)
        results: RCYunetResults = RCYunetResults(results)

        return results
       
