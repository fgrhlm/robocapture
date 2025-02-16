# https://docs.python.org/3/howto/sockets.html
# https://docs.python.org/3/library/queue.html#queue.SimpleQueue

import socket
import sys
import queue

from utils.logger import logger, LogLevel

class APISocket:
    def __init__(self, port=8001):
        self.stop = False
        self.port = port
         
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error as e:
            logger("APISocket", f"Could not create socket: {e}", level=LogLevel.FATAL)
            logger("APISocket", f"Terminating! Goodbye!", level=LogLevel.FATAL)
            exit(1)

        self.socket.bind(("", self.port))

    def listen(self,_queue=None):
        self.socket.listen(5)
        logger("APISocket", f"Listening on {self.port}..")
        
        while not self.stop:
            client_socket, client_addr = self.socket.accept()
            logger("APISocket", f"{client_addr[0]} connected!")

            if not _queue:
                continue

            while True:
                try:
                    # Pop result from the queue
                    payload = _queue.get()

                    payload.replace(" ","")
                    payload.replace("\t","")
                    payload.replace("\n","")
                    
                    # Strip string
                    payload = payload.encode()
                   
                    try:
                        # Send the payload
                        client_socket.sendall(payload)

                        # Signal next
                        payload_next = "\n\n\n".encode()
                        client_socket.sendall(payload_next)

                    except ConnectionResetError:
                        logger("APISocket", f"Client {client_addr[0]} disconnected!")
                        break
                    except Exception as e:
                        logger("APISocket", f"Socket error: {e}", level=LogLevel.FATAL)
                        break
                        
                except queue.Empty:
                        continue

            client_socket.close()
            break

        logger("APISocket", f"Goodbye!")
