import cv2 as cv
import numpy as np
import sys
import sounddevice as sd
import soundfile as sf
import tempfile

from collections.abc import Callable
from threading import Event
from queue import Queue

from utils.logger import logger, LogLevel

# https://github.com/spatialaudio/python-sounddevice/blob/0.5.1/examples/rec_unlimited.py
# https://github.com/davabase/whisper_real_time/blob/master/transcribe_demo.py
# https://python-sounddevice.readthedocs.io/en/0.5.1/examples.html
# https://python-soundfile.readthedocs.io/en/0.13.1/#soundfile-objects

class RCAudioCapture:
    def __init__(self,device=0,channels=1,sample_rate=16000,clip_len=1):
        self.device = 0
        self.channels = channels
        self.sample_rate = sample_rate
        self.clip_len = clip_len

    def process(self, f: Callable, stop_event: Event = None):
        logger("RCAudioCapture", "Processing..")

        while not stop_event.is_set():
            try:
                clip = sd.rec(int(self.sample_rate * self.clip_len), samplerate=self.sample_rate, channels=self.channels, blocking=True)
            except:
                print("GHEW")
            clip = clip.flatten()

            f(clip)

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
