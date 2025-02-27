import cv2 as cv
import sys
import pyaudio

from collections.abc import Callable
from threading import Event

from utils.logger import logger, LogLevel

class RCAudioCapture:
    def __init__(
        self,
        format = pyaudio.paInt16,
        channels: int = 1,
        sample_rate: int = 48000,
        frames_per_buffer: int = 1024,
        input_device: int = 57,
        rec_len: int = 3
    ):
        self.format = format
        self.channels = channels
        self.sample_rate = sample_rate
        self.frames_per_buffer = frames_per_buffer
        self.input_device = input_device
        self.rec_len = rec_len
        self.target_len = ((sample_rate / frames_per_buffer) * self.rec_len)
        self.input = pyaudio.PyAudio()
        self.cap = self.open()

    def open(self):
        try:
            cap = self.input.open(
                format = self.format,
                channels = self.channels,
                rate = self.sample_rate,
                input = True,
                frames_per_buffer = self.frames_per_buffer,
            )

            logger("RCAudioCapture", "Capture opened!")

            return cap
        except:
            logger("RCAudioCapture", "Cant open audio capture!", level=LogLevel.FATAL)
            sys.exit(1)

    def close(self):
        self.cap.stop_stream()
        self.cap.close()
        self.input.terminate()

        logger("RCAudioCapture", "Capture closed!")

    def process(self, f: Callable, stop_event: Event = None):
        logger("RCAudioCapture", "Processing..")

        while not stop_event.is_set():
            data = []
            
            while len(data) < self.target_len:
                sample = self.cap.read(self.frames_per_buffer)
                data.append(sample)

            # Process data
            f(data)

        self.close()


class RCVideoCapture:
    """Thin wrapper around OpenCV's VideoCapture, with some additional functionality."""
    def __init__(self, dev: str):
        """Opens a capture. **`cap`** is the source device."""
        self.frame_width: int = 0
        """Capture frame width"""

        self.frame_height: int = 0
        """Capture frame height"""

        self.cap: cv.VideoCapture = self.open(dev)
        """
        OpenCV VideoCapture object

        https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html

        """
        self.fps = 0

    def open(self, path: str) -> cv.VideoCapture:
        """
        Opens an OpenCV VideoCapture

        https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html

        """
        try:
            cap: cv.VideoCapture = cv.VideoCapture(path)
            self.frame_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
            self.frame_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
            logger("RCVideoCapture", "Capture opened!")
        except:
            logger("RCVideoCapture", "Could not open VideoCapture.",level=LogLevel.FATAL)
            sys.exit(1)
        
        return cap
    
    def close(self) -> None:
        """Close capture"""
        self.cap.release()

    def process(self, f: Callable, stop_event: Event=None):
        logger("RCVideoCapture", "Processing..")

        """Executes function **`f(frame)`** every new frame"""
        tm = cv.TickMeter()

        while self.cap.isOpened() and not stop_event.is_set():
            tm.start()
            ret, frame = self.cap.read()

            if not ret:
                self.cap.set(cv.CAP_PROP_POS_FRAMES, 0)
                continue
            
            f(frame)

            if cv.waitKey(1) == ord('x'):
                break
            
            tm.stop()
            self.fps = tm.getFPS()

        self.close()
