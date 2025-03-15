import sys
import json
import logging

from time import thread_time
from worker import RCWorker
from queue import Queue, Empty
from threading import Event
from websockets.sync.server import serve

# https://websockets.readthedocs.io/en/stable/index.html

class RCWebSocket(RCWorker):
    """Pops detection results of a queue and serves them to clients via a websocket"""
    def __init__(self, config, queue):
        RCWorker.__init__(self, "socket", config.get("socket"), queue)
        self.server_config = config
        self.port = self.config["port"] or 9001
        self.socket = None

        #disable logging
        logging.getLogger("websockets").addHandler(logging.NullHandler())
        logging.getLogger("websockets").propagate = False

    def preprocess_payload(self, data) -> str:
        """Serializes, cleans up, and encodes the payload."""

        payload: str = json.dumps(data)

        # Clean up string
        payload.replace(" ","")
        payload.replace("\t","")
        payload.replace("\n","")

        return payload

    def run(self):
        """Accept connections, processes detection results and sends payload to client."""
        logging.info(f"Listening on {self.port}..")

        def handler(ws):
            logging.debug("Client connected!")

            init_payload = self.preprocess_payload([{
                "name": "server_config",
                "data": self.server_config.json
            }])

            try:
                ws.send(init_payload)

                while True:
                    if self.stop_signal:
                        break

                    payload = self.queue.get()
                    payload = self.preprocess_payload(payload)

                    ws.send(payload)
            except Exception as e:
                print(e)

            logging.debug("Client disconnecting!")

        with serve(handler, "localhost", self.port) as server:
            self.socket = server
            server.serve_forever()

        logging.info("RCWebSocket stopped!")
