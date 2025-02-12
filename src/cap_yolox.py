import sys
import cv2 as cv
import numpy as np

from capture import RCVideoCapture
from ultralytics import YOLO

# https://docs.opencv.org/4.x/d0/dd4/tutorial_dnn_face.html

if __name__=="__main__":
    if len(sys.argv) != 2:
        exit()

    yolox_model_path = sys.argv[1]

    cap = RCVideoCapture()
    cap.from_file("media/test.mp4")

    # Yolox load
    yolox_model = YOLO(yolox_model_path)

    # Inference
    def infer(frame):
        yolox_results = yolox_model(frame,verbose=False)
        yolox_plot = yolox_results[0].plot()

        cv.imshow("test", yolox_plot)

    cap.process(infer)

    cv.destroyAllWindows()
