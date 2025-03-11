import sys
import ext
import logging

from threading import Thread, Event
from queue import Queue
from sock import RCWebSocket
from config import RCConfig
from video import RCVideo
from time import sleep

if __name__=="__main__":
    if len(sys.argv) < 2:
        print("Arguments missing!")
        sys.exit()

    config_path = sys.argv[1]
    config = RCConfig(config_path)

    on_data = ext.load_modules(config, "on_data")
    on_save = ext.load_modules(config, "on_save")

    share = Queue()

    w_video = RCVideo(config, share, on_data=on_data, on_save=on_save)
    w_server = RCWebSocket(config.get("server"), share)

    t_video = Thread(target=w_video.run)
    t_server = Thread(target=w_server.run)

    t_video.start()
    t_server.start()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt as e:
        logging.info("User requested termination <CTRL-C>")
        w_video.stop()
        w_server.stop()
        w_server.socket.shutdown()

    logging.info("Bye!")

