import cv2 as cv

from utils.logger import logger

class RCVideoCapture:
    def __init__(self, cap):
        self.device = None
        self.frame_width = 0
        self.frame_height = 0
        self.cap = self.open(cap)
        self.fps = 0

    def open(self, path):
        cap = cv.VideoCapture(path)
        self.frame_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        
        return cap

    def process(self, f, _queue=None):
        tm = cv.TickMeter()

        while self.cap.isOpened():
            tm.start()
            ret, frame = self.cap.read()

            if not ret:
                break
            
            f(frame,_queue=_queue)

            if cv.waitKey(1) == ord('x'):
                break
            
            tm.stop()
            self.fps = tm.getFPS()

        self.cap.release()
