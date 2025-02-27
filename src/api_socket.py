# https://docs.python.org/3/howto/sockets.html
# https://docs.python.org/3/library/queue.html#queue.SimpleQueue
import sys
import json

from queue import Queue, Empty
from threading import Event
from websockets.sync.server import serve

from result import RCYoloResults, RCYunetResults
from utils.logger import logger, LogLevel

class APISocket:
    """Pops detection results of a queue and serves them to clients via a websocket"""
    def __init__(self, port: int = 8001):
        self.port = port 

    def preprocess_payload(self, audio, video, frame) -> str:
        """Serializes, cleans up, and encodes the payload."""

        # Serialize payload dict to json string
        payload = {
            "yolo": [{
                "name": n.class_name,
                "conf": n.confidence,
                "box": [n.box.x1, n.box.y1, n.box.x2, n.box.y2]
            } for n in video[0].processed],
            "yunet": [{
                "name": n.class_name,
                "conf": n.confidence,
                "box": [n.box.x1, n.box.y1, n.box.x2, n.box.y2]
            } for n in video[1].processed],
            "frame": frame,
            "meta": video[2]
        } 

        payload: str = json.dumps(payload)

        # Clean up string
        payload.replace(" ","")
        payload.replace("\t","")
        payload.replace("\n","")
        
        return payload

    def start_socket(
            self,
            audio_results_queue: Queue=None,
            video_results_queue: Queue=None,
            frames_queue: Queue=None,
            stop_event: Event=None
    ):
        """Accept connections, processes detection results and sends payload to client."""
        logger("APISocket", f"Listening on {self.port}..")

        def handler(ws):
            while not stop_event.is_set():
                if not results_queue:
                    continue
                # Pop detection results from the queue and send them to client.
                while not stop_event.is_set():
                    try:
                        next_audio: dict = video_results_queue.get()
                        next_video: dict = audio_results_queue.get()
                        next_frame: str = frames_queue.get()
                        
                        payload: str = self.preprocess_payload(next_audio, next_video, next_frame)
                        
                        try:
                            ws.send(payload)
                        except Exception as e:
                            break
                    except Empty:
                        break

        with serve(handler, "localhost", self.port) as server:
            server.serve_forever()

        logger("APISocket", f"Goodbye!")
