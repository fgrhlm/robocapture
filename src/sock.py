import sys
import json
import logging

from queue import Queue, Empty
from threading import Event
from websockets.asyncio.server import serve

# https://websockets.readthedocs.io/en/stable/index.html

class RCWebSocket:
    """Pops detection results of a queue and serves them to clients via a websocket"""
    def __init__(self, config, stop_event, audio_queue, video_queue):
        self.config = config
        self.stop_event = stop_event
        self.port = self.config["port"] or 9001
        self.audio_queue = audio_queue
        self.video_queue = video_queue

        #disable logging
        logging.getLogger("websockets").addHandler(logging.NullHandler())
        logging.getLogger("websockets").propagate = False

    def preprocess_payload(self, data) -> str:
        """Serializes, cleans up, and encodes the payload."""

        payload = {n.name:n.data for n in data}
        payload: str = json.dumps(payload)

        # Clean up string
        payload.replace(" ","")
        payload.replace("\t","")
        payload.replace("\n","")
        
        return payload

    async def start(self):
        """Accept connections, processes detection results and sends payload to client."""
        logging.info(f"Listening on {self.port}..")

        async def handler(ws):
            logging.debug("Client connected!")
            while True:
                if self.stop_event.is_set():
                    break

                if self.config["audio"] == True and not self.audio_queue.empty():    
                    next_audio = self.audio_queue.get_nowait()
                    if len(next_audio.data) > 1:
                        payload = self.preprocess_payload(next_audio)
                        await ws.send(payload)

                if self.config["video"] == True and not self.video_queue.empty():
                    next_video = self.video_queue.get()
                    payload = self.preprocess_payload(next_video)
                    await ws.send(payload)

        async with serve(handler, "localhost", self.port) as server:
            await server.serve_forever()
