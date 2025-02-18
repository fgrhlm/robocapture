import sys
import cv2 as cv
import numpy as np

from capture import RCVideoCapture

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

    def detect(self, frame):
        results = self.model.detect(frame)
       
        try:
            r = []
            if results[0] > 1:
                for n in results[1]:
                    r.append({"face": float(n[-1])})
        except TypeError:
            print(type(results))
            print(results)

        return r
