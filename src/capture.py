import cv2 as cv

class RCVideoCapture:
    def __init__(self, cap):
        self.device = None
        self.frame_width = 0
        self.frame_height = 0
        self.cap = self.open(cap)

    def open(self, path):
        cap = cv.VideoCapture(path)
        self.frame_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        
        return cap

    def process(self, f):
        print(f"Capture\n  Frame Width: {self.frame_width}\n  Frame Height: {self.frame_height}")
        
        tm = cv.TickMeter()

        while self.cap.isOpened():
            tm.start()
            ret, frame = self.cap.read()

            if not ret:
                break
            
            f(frame)
            tm.stop()
            print(tm.getFPS())

            if cv.waitKey(1) == ord('x'):
                break

        self.cap.release()
