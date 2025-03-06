import sys
import os
import json
import numpy as np
import logging

from time import sleep
from importlib import import_module
from queue import Queue
from threading import Event, Thread

from config import RCConfig
from audio import RCAudioThread
from video import RCVideoThread

# https://docs.python.org/3/library/threading.html
# https://www.geeksforgeeks.org/multithreading-python-set-1/
# https://docs.python.org/3/library/queue.html#queue.SimpleQueue

class RCServer:
    def __init__(self, config_path):
        self.config = RCConfig(config_path)

        self.config_audio = self.config.get("audio")
        self.config_video = self.config.get("video")
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
        logging.info("Starting worker threads..")
        for thread in self.threads:
            thread.start()

            while not thread.is_ready():
                sleep(0.5)
    
    def join_workers(self):
        while True in [n.is_alive() for n in self.threads]:
            for t in self.threads:
                t.join(1)
            
    def run(self):
        logging.info("Starting server..")
        self.start_workers()

        while True:
            if self.stop_event.is_set():
                break

            sleep(1)

if __name__=="__main__":
    try:
        config_path = sys.argv[1]
        server = RCServer(config_path)
        server.run()
    except KeyboardInterrupt:
        server.stop_event.set()
        server.join_workers()
