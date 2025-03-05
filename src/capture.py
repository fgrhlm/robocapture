import cv2 as cv
import numpy as np
import sys
import os
import sounddevice as sd
import soundfile as sf


from tempfile import mkdtemp
from collections.abc import Callable
from threading import Event
from queue import Queue
from enum import Enum

from utils.logger import logger, LogLevel

# https://python-soundfile.readthedocs.io/
# https://python-sounddevice.readthedocs.io/
# https://github.com/spatialaudio/python-sounddevice/blob/0.5.1/examples/rec_unlimited.py
# https://github.com/davabase/whisper_real_time/blob/master/transcribe_demo.py
# https://python-sounddevice.readthedocs.io/en/0.5.1/examples.html
# https://python-soundfile.readthedocs.io/en/0.13.1/#soundfile-objects
# https://stackoverflow.com/questions/40138031/how-to-read-realtime-microphone-audio-volume-in-python-and-ffmpeg-or-similar
# https://stackoverflow.com/questions/26541416/generate-temporary-file-names-without-creating-actual-file-in-python

class RCAudioCaptureState(Enum):
    STOPPED = 0
    WRITING = 1
    LISTENING = 2

class RCAudioCapture:
    def __init__(self,
        config,
        device=sd.default.device,
        sample_rate=16000,
        channels=1,
        blksize=128,
        rec_threshold=0.0,
    ):
        self.device = device
        self.sample_rate = sample_rate
        self.channels = channels
        self.blksize = blksize
        self.rec_threshold = rec_threshold
        self.state = RCAudioCaptureState.STOPPED
        self.level = 0
        self.buffer = Queue()
        self.stream = sd.InputStream(
            blocksize=blksize,
            samplerate=self.sample_rate,
            device=self.device,
            channels=channels,
            callback=self.callback
        )

    def process(self, clips_queue, f = None, stop_event: Event = None):
        self.stream.start()
        tmp_dir = mkdtemp()

        logger("RCAudioCapture", "Processing..")
        while not stop_event.is_set():
            clip_fn = os.path.join(tmp_dir, f"{}.wav")
            with sf.SoundFile(
                clip_fn,
                "w",
                channels=self.channels,
                samplerate=self.sample_rate,
                format="WAV"
            ) as file:
                while True:
                    data = self.buffer.get()

                    if not data.any():
                        continue

                    if f is not None:
                        f(data)

                    if self.state == RCAudioCaptureState.WRITING:
                        file.write(data)
                        continue
                    
                    if file.tell() > 0:
                        break
            
                clips_queue.put(clip_fn)
       
        os.rmdir(tmp_dir)
        self.stream.stop()
    
    def callback(self, data, frames, time, status):
        data_cpy = data.copy()
        
        self.level = np.linalg.norm(data_cpy)

        if (self.level < self.rec_threshold):
            self.state = RCAudioCaptureState.LISTENING
        else:
            self.state = RCAudioCaptureState.WRITING
            self.buffer.put(data_cpy)

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
