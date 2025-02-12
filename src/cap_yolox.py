import sys
import cv2 as cv
import numpy as np

from capture import RCVideoCapture
from ultralytics import YOLO

# https://docs.opencv.org/4.x/d0/dd4/tutorial_dnn_face.html
# https://docs.ultralytics.com/modes/predict/
# https://www.geeksforgeeks.org/object-detection-with-yolo-and-opencv/

if __name__=="__main__":
    if len(sys.argv) != 2:
        exit()

    yolox_path = sys.argv[1]

    cap = RCVideoCapture("media/test.mp4")
    yolox = YOLO(yolox_path)

    # Inference
    def infer(frame):
        results = yolox(frame, verbose=False)
        plot = results[0].plot()

        cv.imshow("YOLOX", plot)

    cap.process(infer)

    cv.destroyAllWindows()
