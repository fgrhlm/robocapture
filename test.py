import numpy as np
import sounddevice as sd
import soundfile as sf

from queue import Queue
from time import sleep

DEVICE=0
RATE=16000
CHANNELS=1
BLKSIZE=128
REC_LEN=4
MAX_SIZE=(RATE*REC_LEN) / BLKSIZE
REC_THRESHOLD=1.0
REC_STOP_DELAY=2.0

audio_buf = Queue(maxsize=MAX_SIZE)
rec_stop_timer = 0

def rec_threshold(data):
    # https://stackoverflow.com/questions/40138031/how-to-read-realtime-microphone-audio-volume-in-python-and-ffmpeg-or-similar
    level = np.linalg.norm(data) 

    return level >= REC_THRESHOLD

def sd_cb(data, frames, time, status):
    data_copy = data.copy()

    if rec_threshold(data_copy):
        print("Recording..")
        audio_buf.put(data_copy) 
    else:
        if rec_stop_timer >= (RATE*REC_LEN):
            is_recording = False

if __name__=="__main__":
    rec_fn = "test.wav"
    stream = sd.InputStream(blocksize=BLKSIZE,samplerate=RATE, device=DEVICE, channels=CHANNELS, callback=sd_cb)

    print("Starting stream")
    stream.start()

    while True:
        with sf.SoundFile(rec_fn, mode="w", samplerate=RATE, channels=CHANNELS) as file:
            while True:
                if audio_buf.empty() and file.frames > 0:
                    break

                data = audio_buf.get()
                file.write(data)
        
        print(f"Saved to: {rec_fn}")
