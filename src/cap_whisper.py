import whisper
import torch
import numpy as np

from utils.logger import logger, LogLevel
from result import RCWhisperResults

class RCWhisper:
    def __init__(self, config: dict):
        self.model = whisper.load_model("tiny")

    def detect(self, clip):
        logger("RCWhisper", "Detecting..")
       
        clip = whisper.pad_or_trim(clip)

        mel = whisper.log_mel_spectrogram(clip, n_mels=self.model.dims.n_mels).to(self.model.device)
        options = whisper.DecodingOptions()
        result = whisper.decode(self.model, mel, options)
        print(result.text)

        results: RCWhisperResults = RCWhisperResults(result)
        return results
        

