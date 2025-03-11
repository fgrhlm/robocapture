import sys
import ext
import importlib
import logging

from time import sleep
from threading import Thread
from queue import Queue
from sock import RCWebSocket
from config import RCConfig

# https://www.geeksforgeeks.org/how-to-dynamically-load-modules-or-classes-in-python/
# https://stackoverflow.com/questions/67631/how-can-i-import-a-module-dynamically-given-the-full-path
# https://docs.python.org/3/library/dataclasses.html
# https://stackoverflow.com/questions/47558704/python-dynamic-import-methods-from-file
# https://stackoverflow.com/questions/29269370/how-to-properly-create-and-run-concurrent-tasks-using-pythons-asyncio-module

class RCServer:
    def __init__(self, config):
        self.config = config
        self.on_data = ext.load_modules(config, "on_data")
        self.on_save = ext.load_modules(config, "on_save")

        self.share = Queue()

        match self.config.get("server_type"):
            case "audio":
                self.worker = importlib.import_module("audio")
            case "video":
                self.worker = importlib.import_module("video")
            case _:
                logging.error(f"Invalid server_type, bye!")
                sys.exit(1)

        self.worker = self.worker.new(
            self.config,
            self.share,
            self.on_data,
            self.on_save
        )

        self.socket = RCWebSocket(
            self.config.get("socket"),
            self.share
        )

        self.t_worker = Thread(target=self.worker.run)
        self.t_socket = Thread(target=self.socket.run)

    def start(self):
        self.t_worker.start()
        self.t_socket.start()

        try:
            while True:
                sleep(1)
        except KeyboardInterrupt as e:
            logging.info("User requested termination <CTRL-C>")
            self.worker.stop()
            self.socket.stop()
            self.socket.socket.shutdown()

        logging.info("Bye!")


