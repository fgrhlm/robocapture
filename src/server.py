import sys
import os
import json
import tomllib
import numpy as np
import logging
import asyncio

from cProfile import Profile
from pstats import Stats
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
# https://docs.python.org/3/library/profile.html
# https://docs.python.org/3/library/profile.html#module-cProfile
# https://docs.python.org/3.7/library/profile.html#pstats.Stats
# https://www.machinelearningplus.com/python/cprofile-how-to-profile-your-python-code/

class RCServer:
    """Manages audio/video worker threads and serves pipeline results."""
    def __init__(self, config_path):
        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)
            self.version = data["project"]["version"]

        print(f"RoboCapture v{self.version}")

        self.config = RCConfig(config_path)
        self.config_server = self.config.get("server")
        self.config_audio = self.config.get("audio")
        self.config_video = self.config.get("video")

        self.config_socket = self.config.get("socket")
        self.config_socket.update({"audio": self.config_audio["enabled"]})
        self.config_socket.update({"video": self.config_video["enabled"]})
       
        # Shared variables (threading)
        self.share = {
            "video": Queue(
                maxsize=None if self.config_server["max_video_queue"] < 1 else self.config_server["max_video_queue"]
            ),
            "audio": Queue(
                maxsize=None if self.config_server["max_audio_queue"] < 1 else self.config_server["max_audio_queue"]
            )
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
            logging.debug(f"Starting: {thread.name}")
            thread.start()
    
    def join_workers(self):
        """Joins worker threads."""
        for t in self.threads:
            t.join(0)
            
    def run(self):
        """Starts the workers and server."""
        logging.info("Starting server..")
        self.start_workers()
     
        for n in self.threads:
            logging.info(f"Waiting for {n.name} to start..")
            while not n.is_ready():
                sleep(0.5)

        sock = RCWebSocket(
            self.config_socket,
            self.stop_event,
            self.share["audio"],
            self.share["video"]
        )

        asyncio.run(sock.start())

def create_rc_home_folder():
    dir_home = os.environ.get("HOME") or "."
    logging.debug(f"User home: {dir_home}")

    dir_rc = os.path.join(dir_home, ".robocapture")

    if not os.path.exists(dir_rc):
        logging.debug(f"Creating: {dir_rc}")
        os.mkdir(dir_rc)

    tree = [
        "models",
        "logs",
        "config"
    ]

    print("Creating folders..")
    for folder in tree:
        folder_path = os.path.join(dir_rc, folder)

        if not os.path.exists(folder_path):
            logging.debug(f"Creating: {folder_path}")
            os.mkdir(folder_path)

    return dir_rc

def handle_args():
    if len(sys.argv) < 2:
        print("Error! Missing arguments!")
        usage()

    _args = {
        "config": sys.argv[1]
    }

    logging.debug(_args)

    return _args

def usage():
    print("usage: rcserver <path-to-config>")
    sys.exit(1)

def start_server(in_args):
    run_profiler = os.environ.get("RC_CPROFILE") or False
    logging.debug(f"Run with profiler: {'YES' if run_profiler else 'NO'}")

    home_dir = in_args["home_dir"]
    logging.debug(f"Home folder: {home_dir}")
   
    if run_profiler:
        profiler = Profile()
        profiler.enable()
        logging.debug("cProfile enabled!")

    try:
        config_path = in_args["config"]
        server = RCServer(config_path)
        server.run()
    except KeyboardInterrupt:
        server.stop_event.set()
        server.join_workers()

    if run_profiler:
        profiler.disable()
        logging.debug("cProfile disabled!")
        
        out_path = os.path.join(home_dir, "logs", "cprofile.out")
        logging.debug(f"Saving cProfile output to: {out_path}")
        
        stats = Stats(profiler)
        stats.dump_stats(out_path) 

if __name__=="__main__":
    in_args = handle_args()

    home_dir = create_rc_home_folder()
    in_args.update({"home_dir": home_dir})

    start_server(in_args)
    
    logging.info("Bye!")
