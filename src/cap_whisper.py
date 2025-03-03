import whisper
import torch
import numpy as np

from utils.logger import logger, LogLevel
from result import RCWhisperResults

class RCWhisper:
    def __init__(self, config: dict):
        self.model = whisper.load_model("tiny.en")

    def detect(self, clip):
        #clip = whisper.load_audio(clip)
        #clip = whisper.pad_or_trim(clip)

        logger("RCWhisper", "Detecting..")
        #mel = whisper.log_mel_spectrogram(clip, n_mels=self.model.dims.n_mels).to(self.model.device)
        #options = whisper.DecodingOptions()
        #result = whisper.decode(self.model, mel, options)
        result = self.model.transcribe(clip)
        print(result)

        results: RCWhisperResults = RCWhisperResults(result)
        return results
        

