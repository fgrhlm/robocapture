import sys
import os
import json
import tomllib
import numpy as np
import logging

from time import sleep
from importlib import import_module
from queue import Queue
from threading import Event, Thread

from config import RCConfig
from audio import RCAudioThread
from video import RCVideoThread
from sock import RCWebSocket

# https://docs.python.org/3/library/threading.html
# https://www.geeksforgeeks.org/multithreading-python-set-1/
# https://docs.python.org/3/library/queue.html#queue.SimpleQueue


class RCServer:
    """Manages audio/video worker threads and serves pipeline results."""
    def __init__(self, config_path):
        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)
            self.version = data["project"]["version"]

        print(f"RoboCapture v{self.version}")

        self.config = RCConfig(config_path)
        self.config_audio = self.config.get("audio")
        self.config_video = self.config.get("video")
        self.config_socket = self.config.get("socket")
        self.config_api = self.config.get("api")
       
        # Shared variables (threading)
        self.share = {
            "video": Queue(),
            "audio": Queue()
        }

        self.stop_event = Event()

        # Threads
        self.threads = []

        if self.config_audio.get("enabled"): 
            self.threads.append(
                RCAudioThread(
                    self.config_audio,
                    self.stop_event,
                    self.share.get("audio")
                )
            )

        if self.config_video.get("enabled"): 
            self.threads.append(
                RCVideoThread(
                    self.config_video,
                    self.stop_event,
                    self.share.get("video")
                )
            )

    def start_workers(self):
        """Starts worker threads."""
        logging.info("Starting worker threads..")
        for thread in self.threads:
            thread.start()

            while not thread.is_ready():
                sleep(0.5)
    
    def join_workers(self):
        """Joins worker threads."""
        while True in [n.is_alive() for n in self.threads]:
            for t in self.threads:
                t.join(1)
            
    def run(self):
        """Starts the workers and server."""
        logging.info("Starting server..")
        self.start_workers()
        
        sock = RCWebSocket(
            self.config_socket,
            self.stop_event,
            self.share["audio"],
            self.share["video"]
        )

        sock.start()

if __name__=="__main__":
    if len(sys.argv) < 2:
        print("Please provide path to config.")
        print("usage: rcserver <path-to-config>")
        sys.exit(1)

    try:
        config_path = sys.argv[1]
        server = RCServer(config_path)
        server.run()
    except KeyboardInterrupt:
        server.stop_event.set()
        server.join_workers()
