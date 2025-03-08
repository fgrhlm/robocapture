import whisper
import logging
import numpy as np

from pipeline import RCPipelineResult

class RCWhisper:
    def __init__(self, config: dict):
        self.name = "whisper"
        self.config = config["ext"]["whisper"]

        logging.info(f"Loading whisper model {self.config['checkpoint']}..")
        self.model = whisper.load_model(self.config["checkpoint"])

    def process(self, clip):
        #clip = whisper.load_audio(clip)
        #clip = whisper.pad_or_trim(clip)

        logging.debug(f"Detecting: {clip}")
        #mel = whisper.log_mel_spectrogram(clip, n_mels=self.model.dims.n_mels).to(self.model.device)
        #options = whisper.DecodingOptions()
        #result = whisper.decode(self.model, mel, options)
        try:
            result = self.model.transcribe(clip)
        except Exception as e:
            logging.error(f"Could not transcribe: {clip}")

        results = RCPipelineResult("whisper", result)

        return results

step = RCWhisper
