import cv2 as cv

class RCVideoCapture:
    def __init__(self):
        self.device = None
        self.frame_width = 0
        self.frame_height = 0
        self.cap = None

    def _cap_meta(self, device):
        self.device = device
        self.frame_width = int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT))

    def from_file(self, path):
        self.cap = cv.VideoCapture(path)
        self._cap_meta(self.device)

    def from_device(self, device):
        self.cap = cv.VideoCapture(device)
        self._cap_meta(self.device)

    def process(self, f):
        print(f"Capture\n  Frame Width: {cap.frame_width}\n  Frame Height: {cap.frame_height}")
        
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
