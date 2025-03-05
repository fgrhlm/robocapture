import sys
import json

from queue import Queue, Empty
from threading import Event
from websockets.sync.server import serve

from result import RCYoloResults, RCYunetResults
from utils.logger import logger, LogLevel

# https://websockets.readthedocs.io/en/stable/index.html

class APISocket:
    """Pops detection results of a queue and serves them to clients via a websocket"""
    def __init__(self, port: int = 8001):
        self.port = port 

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

    def start_socket(
            self,
            audio_queue: Queue = None,
            video_queue: Queue = None,
            stop_event: Event=None
    ):
        """Accept connections, processes detection results and sends payload to client."""
        logger("APISocket", f"Listening on {self.port}..")

        def handler(ws):
            print("Connection!")
            while not stop_event.is_set():
                while True:
                    try:
                        next_audio = audio_queue.get()
                        next_video = video_queue.get()
                    except:
                        print("Could not get data")
                        
                    payload: str = self.preprocess_payload(
                        next_audio,
                        next_video
                    )
                        
                    try:
                        ws.send(payload)
                    except Exception as e:
                        print("Could not send payload")
                        break

            print("Connection goodbye!")

        with serve(handler, "localhost", self.port) as server:
            server.serve_forever()

        logger("APISocket", f"Goodbye!")
