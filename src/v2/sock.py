import sys
import json
import logging

from queue import Queue, Empty
from threading import Event
from websockets.sync.server import serve

# https://websockets.readthedocs.io/en/stable/index.html

class RCWebSocket:
    """Pops detection results of a queue and serves them to clients via a websocket"""
    def __init__(self, config, stop_event, audio_queue, video_queue):
        self.config = config
        self.stop_event = stop_event
        self.port = self.config["port"] or 9001
        self.audio_queue = audio_queue
        self.video_queue = video_queue

    def preprocess_payload(self, audio, video) -> str:
        """Serializes, cleans up, and encodes the payload."""

        # Serialize payload dict to json string
        payload = {
            "audio": audio,
            "video": video
        }

        payload: str = json.dumps(payload)

        # Clean up string
        payload.replace(" ","")
        payload.replace("\t","")
        payload.replace("\n","")
        
        return payload

    def start(self):
        """Accept connections, processes detection results and sends payload to client."""
        logging.info(f"Listening on {self.port}..")

        def handler(ws):
            logging.debug("Client connected!")
            while True:
                if self.stop_event.is_set():
                    break

                try:
                    next_audio = audio_queue.get()
                    next_video = video_queue.get()
                except Exception as e:
                    logging.warn(f"Could not get data from queue! {e}")
                    
                payload: str = self.preprocess_payload(
                    next_audio,
                    next_video
                )
                    
                try:
                    ws.send(payload)
                except Exception as e:
                    logging.error("Could not send payload")
                    break

        with serve(handler, "localhost", self.port) as server:
            server.serve_forever()
