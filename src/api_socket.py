# https://docs.python.org/3/howto/sockets.html
# https://docs.python.org/3/library/queue.html#queue.SimpleQueue
import sys
import json

from queue import SimpleQueue, Empty
from threading import Event
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

from result import RCYoloResults, RCYunetResults
from utils.logger import logger, LogLevel

class APISocket:
    """Pops detection results of a queue and serves them to clients via a TCP socket"""
    def __init__(self, port: int = 8001):
        self.port: int = port
        """Which port the socket should listen to."""
         
        try:
            self.socket: socket = socket(AF_INET, SOCK_STREAM)
            """Socket object"""
            self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.socket.settimeout(1)
        except socket.error as e:
            logger("APISocket", f"Could not create socket: {e}", level=LogLevel.FATAL)

        self.socket.bind(("", self.port))

    def preprocess_payload(self, payload: list[RCYoloResults, RCYunetResults]) -> bytes:
        """Serializes, cleans up, and encodes the payload."""

        # Serialize payload dict to json string
        payload = {
            "yolo": [{
                "name": n.class_name,
                "conf": n.confidence,
                "box": [n.box.x1, n.box.y1, n.box.x2, n.box.y2]
            } for n in payload[0].processed],
            "yunet": [{
                "name": n.class_name,
                "conf": n.confidence,
                "box": [n.box.x1, n.box.y1, n.box.x2, n.box.y2]
            } for n in payload[1].processed],
        } 

        payload: str = json.dumps(payload)

        # Clean up string
        payload.replace(" ","")
        payload.replace("\t","")
        payload.replace("\n","")
        
        # Encode for sending
        payload: bytes = payload.encode()

        return payload

    def send_payload(self, client: socket, payload: bytes) -> None:
        """Sends the payload."""

        # Send the payload
        client.sendall(payload)

        # Signal end of message to client
        payload_next: bytes = "\n\n\n".encode()
        client.sendall(payload_next)

    def start(self,results_queue: SimpleQueue=None,stop_event: Event=None):
        """Accept connections, processes detection results and sends payload to client."""

        self.socket.listen(5)
        logger("APISocket", f"Listening on {self.port}..")
        
        while not stop_event.is_set():
            client_socket: socket = None
            client_addr: str = None

            # Try to accept connection
            try:
                client_socket, client_addr = self.socket.accept()
                if not client_socket:
                    continue
            except TimeoutError as e:
                continue
            except Exception as e:
                logger("APISocket", f"Socket error: {e}")
                continue
            
            if not client_socket or not client_addr:
                continue

            logger("APISocket", f"{client_addr[0]} connected!")

            if not results_queue:
                continue

            # Pop detection results from the queue and send them to client.
            while not stop_event.is_set():
                try:
                    next_results: dict = results_queue.get()

                    payload: bytes = self.preprocess_payload(next_results)
                               
                    try:
                        self.send_payload(client_socket, payload)
                    except ConnectionResetError:
                        logger("APISocket", f"{client_addr[0]} connection reset!")
                        break
                    except BrokenPipeError:
                        logger("APISocket", f"{client_addr[0]} broken pipe!")
                        break

                except Empty:
                        continue

            client_socket.close()
            break

        logger("APISocket", f"Goodbye!")
