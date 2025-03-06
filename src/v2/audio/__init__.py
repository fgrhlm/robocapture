import os
import sys
import logging
import numpy as np

from uuid import uuid1
from enum import Enum
from pipeline import RCPipeline
from sounddevice import InputStream
from soundfile import SoundFile
from queue import Queue
from tempfile import mkdtemp
from threads import RCThread

# https://numpy.org/doc/stable/reference/generated/numpy.fft.fft.html
# https://stackoverflow.com/questions/4315989/python-frequency-analysis-of-sound-files
# https://python-soundfile.readthedocs.io/
# https://python-sounddevice.readthedocs.io/
# https://github.com/spatialaudio/python-sounddevice/blob/0.5.1/examples/rec_unlimited.py
# https://github.com/davabase/whisper_real_time/blob/master/transcribe_demo.py
# https://python-sounddevice.readthedocs.io/en/0.5.1/examples.html
# https://python-soundfile.readthedocs.io/en/0.13.1/#soundfile-objects
# https://stackoverflow.com/questions/40138031/how-to-read-realtime-microphone-audio-volume-in-python-and-ffmpeg-or-similar
# https://stackoverflow.com/questions/26541416/generate-temporary-file-names-without-creating-actual-file-in-python

class RCAudioState(Enum):
    STOPPED = 0
    WRITING = 1
    LISTENING = 2
    PIPELINE_EXEC = 3

class RCAudio:
    def __init__(self, config, stop_event, out_queue):
        self.config = config
        self.stop_event = stop_event

        self.state = RCAudioState.STOPPED
        self.level = 0

        self.buffer_queue = Queue()
        self.out_queue = out_queue

        self.device = config["device"] or None
        self.sample_rate = config["sample_rate"] or None
        self.channels = config["channels"] or 1
        self.blksize = config["blksize"] or 128
        self.rec_threshold = 0.6
        
        self.pipeline = RCPipeline(self.config)

        try:
            self.stream = InputStream(
                blocksize = self.blksize,
                samplerate = self.sample_rate,
                device = self.device,
                channels = self.channels,
                callback = self.callback
            ) 
        except Exception as e:
            logging.critical(f"Could not open input stream: {e}")
            self.stop_event.set() 
    
    def get_state(self):
        return self.state

    def set_state(self, state):
        self.state = state

    def callback(self, data, frames, time, status):
        d = data.copy()

        self.level = np.linalg.norm(d)
        
        if self.get_state() != RCAudioState.PIPELINE_EXEC:
            if (self.level < self.rec_threshold):
                self.set_state(RCAudioState.LISTENING)
            else:
                self.set_state(RCAudioState.WRITING)
                self.buffer_queue.put(d)

    def run(self, cb=None):
        logging.info("Starting RCAudio..")
        
        tmp_dir = mkdtemp()
        logging.debug(f"Created tmp dir: {tmp_dir}")

        self.stream.start()

        while True:
            if self.stop_event and self.stop_event.is_set():
                break
            
            clip_name = os.path.join(tmp_dir, f"{uuid1()}.wav")

            with SoundFile(
                clip_name,
                "w",
                channels=self.channels,
                samplerate=self.sample_rate,
                format="WAV"
            ) as file:
                while True:
                    data = self.buffer_queue.get()

                    if not data.any():
                        continue

                    if cb is not None:
                        self.set_state(RCAudioState.PIPELINE_EXEC)
                        self.pipeline.exec("on_data", data)
                        self.set_state(RCAudioState.LISTENING)

                    if self.get_state() == RCAudioState.WRITING:
                        file.write(data)
                        continue
                    
                    if file.tell() > 0:
                        break

                
            self.set_state(RCAudioState.PIPELINE_EXEC)
            self.pipeline.exec("on_save", clip_name)
            self.set_state(RCAudioState.LISTENING)


        logging.info("Stopping RCAudio..")
        self.stream.stop()
        os.rmdir(tmp_dir)

class RCAudioThread(RCThread):
    def __init__(self, config, stop_event, data_queue):
        RCThread.__init__(self, "t_audio", config, stop_event, data_queue)

    def run(self):
        audio = RCAudio(self.config, self.stop_event, self.queue) 

        self.set_ready(True)
        audio.run()
