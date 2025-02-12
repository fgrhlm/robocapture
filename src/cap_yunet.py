import sys
import cv2 as cv
import numpy as np

from capture import RCVideoCapture

def visualize(input, faces):
    thickness = 1

    if faces[1] is not None:
        for idx, face in enumerate(faces[1]):
            coords = face[:-1].astype(np.int32)
            cv.rectangle(input, (coords[0], coords[1]), (coords[0]+coords[2], coords[1]+coords[3]), (0, 255, 0), thickness)
            cv.circle(input, (coords[4], coords[5]), 2, (255, 0, 0), thickness)
            cv.circle(input, (coords[6], coords[7]), 2, (0, 0, 255), thickness)
            cv.circle(input, (coords[8], coords[9]), 2, (0, 255, 0), thickness)
            cv.circle(input, (coords[10], coords[11]), 2, (255, 0, 255), thickness)
            cv.circle(input, (coords[12], coords[13]), 2, (0, 255, 255), thickness)

if __name__=="__main__":
    if len(sys.argv) != 2:
        exit()

    yunet_model_path = sys.argv[1]

    cap = RCVideoCapture()
    cap.from_file("media/test.mp4")

    # Yunet load
    yunet_model = cv.FaceDetectorYN.create(
        yunet_model_path,
        "",
        (320, 320),
        0.6,
        0.3,
        5000
    )

    yunet_model.setInputSize([cap.frame_width, cap.frame_height])

    # Inference
    def infer(frame):
        yunet_results = yunet_model.detect(frame)
        
        visualize(frame, yunet_results)
        cv.imshow("test", frame)

    cap.process(infer)

    cv.destroyAllWindows()
