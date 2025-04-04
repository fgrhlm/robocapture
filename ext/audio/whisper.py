import whisper
import logging
import numpy as np

from src.ext import RCExtWorker

class RCWhisper(RCExtWorker):
    def __init__(self, config: dict):
        RCExtWorker.__init__(self, "whisper", config)
        logging.info(f"Loading whisper model {self.config['weights']}..")
        self.model = whisper.load_model(self.config["weights"],download_root="res")

    def process(self, clip):
        #clip = whisper.load_audio(clip)
        #clip = whisper.pad_or_trim(clip)

        logging.debug(f"Detecting: {clip}")
        #mel = whisper.log_mel_spectrogram(clip, n_mels=self.model.dims.n_mels).to(self.model.device)
        #options = whisper.DecodingOptions()
        #result = whisper.decode(self.model, mel, options)
        try:
            result = self.model.transcribe(clip)
            result = { "lang": result["language"], "text": result["text"] }
        except Exception as e:
            logging.error(f"Could not transcribe: {clip}")

        results = {"name": "whisper", "data": result}

        print(results)

        return results

ext = RCWhisper
