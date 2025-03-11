import whisper
import logging
import numpy as np

class RCWhisper:
    def __init__(self, config: dict):
        self.name = "whisper"
        self.config = config

        logging.info(f"Loading whisper model {self.config['weights']}..")
        self.model = whisper.load_model(self.config["weights"],download_root="models")

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

        results = {"name": "whisper", "data": result}

        return results

ext = RCWhisper
