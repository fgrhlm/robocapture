import os
import sys
import logging
import numpy as np
import ext

from worker import RCWorker
from uuid import uuid1
from enum import Enum
from sounddevice import InputStream
from soundfile import SoundFile
from queue import Queue
from tempfile import mkdtemp
from time import time

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

"""
    TODO:
    - Fix max clip len, defined in config, enforced by checking current file size

"""
class RCAudioState(Enum):
    STOPPED = 0
    WRITING = 1
    LISTENING = 2
    HOLDING = 3
    PIPELINE_EXEC = 4

class RCAudio(RCWorker):
    def __init__(self, config, queue, on_data, on_save):
        RCWorker.__init__(self, "audio", config, queue, on_data=on_data, on_save=on_save)
        self.state = RCAudioState.STOPPED
        self.level = 0
        self.activity = False
        self.device = config.get("device") or None
        self.sample_rate = config.get("sample_rate") or None
        self.channels = config.get("channels") or 1
        self.blksize = config.get("blksize") or 128
        self.rec_threshold = config.get("rec_threshold") or 0.5
        self.rec_hold = config.get("rec_hold") or 0.2
        self.max_clip_len = (self.config.get("max_clip_len") * (self.sample_rate / self.blksize)) or 0
        self.buffer_queue = Queue(maxsize = None if self.max_clip_len < 1 else self.max_clip_len)

        self.timers = {
            "activity_start": 0,
            "activity_end": 0,
        }

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

    def get_state(self):
        return self.state

    def set_state(self, state):
        self.state = state

    def get_hold(self):
        start = self.timers["activity_end"]
        end = time()

        return (end - start) > self.rec_hold

    def callback(self, data, frames, _time, status):
        st = self.get_state()
        if st == RCAudioState.PIPELINE_EXEC:
            return

        d = data.copy()

        self.level = np.linalg.norm(d)
        activity = (self.level > self.rec_threshold)

        if len(self.on_data) > 0:
            on_data_results = ext.run(self.on_data, d)
            self.queue.put(on_data_results)

        if self.activity and not activity:
            self.timers["activity_end"] = time()
            self.set_state(RCAudioState.HOLDING)

        if activity and not self.activity:
            self.timers["activity_start"] = time()
            self.set_state(RCAudioState.WRITING)

        if not activity and not self.activity:
            if self.get_hold():
                self.set_state(RCAudioState.LISTENING)
            else:
                self.set_state(RCAudioState.HOLDING)

        self.activity = activity

        if (st == RCAudioState.WRITING) or (st == RCAudioState.HOLDING):
            try:
                self.buffer_queue.put_nowait(d)
            except Full:
                logging.debug("Audio buffer full!")

    def run(self):
        logging.info("Starting RCAudio..")

        tmp_dir = mkdtemp()
        logging.debug(f"Created tmp dir: {tmp_dir}")

        self.stream.start()

        while not self.stop_signal:
            clip_name = os.path.join(tmp_dir, f"{uuid1()}.wav")

            with SoundFile(
                clip_name,
                "w",
                channels=self.channels,
                samplerate=self.sample_rate,
                format="WAV"
            ) as file:
                while not self.stop_signal:
                    data = self.buffer_queue.get()


                    st = self.get_state()
                    if (st == RCAudioState.WRITING) or (st == RCAudioState.HOLDING):
                        file.write(data)
                        continue

                    if file.tell() > 0:
                        break

            self.set_state(RCAudioState.PIPELINE_EXEC)

            logging.debug(f"New clip ({self.timers["activity_end"] - self.timers["activity_start"]}s): {clip_name}")
            if len(self.on_save) > 0:
                on_save_results = ext.run(self.on_save, clip_name)
                self.queue.put(on_save_results)
            os.remove(clip_name)
            self.set_state(RCAudioState.LISTENING)


        logging.info("Stopping RCAudio..")
        self.stream.stop()
        os.rmdir(tmp_dir)

new = RCAudio
