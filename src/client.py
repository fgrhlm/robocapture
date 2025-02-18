import socket
import sys
import os
import json
from time import sleep

class RoboCaptureClient:
    def __init__(self, addr, port):
        self.stop = False
        self.addr = addr
        self.port = port
        self.socket = socket.socket()
  
    def connect(self):
        while True:
            print("Trying to connect..")

            try:
                self.socket.connect((self.addr, self.port))
                print(f"Connected to {self.addr}:{self.port}!")
                break
            except Exception as e:
                sleep(1)
                print(e)
                continue

    def start(self):
        self.connect()
        while not self.stop:
            try:
                bufsize = 1024

                response = self.socket.recv(bufsize)
                
                while response[-3:] != b'\n\n\n':
                    response += self.socket.recv(bufsize)
                
                response = response.decode()
                
                try:
                    response = json.loads(response)
                    os.system("clear")
                    print("Objects:")
                    for n in response["yolo"]:
                        print(f"{n}")

                    print("\nFaces:")
                    for n in response["yunet"]:
                        print(f"{n}")
                except Exception as e:
                    print(f"EXCEPTION: {e}")
            except KeyboardInterrupt:
                break

        print("Goodbye!")
        self.socket.close()

if __name__=="__main__":
    if len(sys.argv) != 3:
        print("client.py <host> <port>")

    addr = sys.argv[1]
    port = int(sys.argv[2])

    rc = RoboCaptureClient(addr, port)
    rc.start()

