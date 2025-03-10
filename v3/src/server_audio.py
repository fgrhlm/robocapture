import sys
import ext

from threading import Thread
from queue import Queue
from sock import RCWebSocket
from audio import RCAudio
from config import RCConfig

# https://www.geeksforgeeks.org/how-to-dynamically-load-modules-or-classes-in-python/
# https://stackoverflow.com/questions/67631/how-can-i-import-a-module-dynamically-given-the-full-path
# https://docs.python.org/3/library/dataclasses.html
# https://stackoverflow.com/questions/47558704/python-dynamic-import-methods-from-file
# https://stackoverflow.com/questions/29269370/how-to-properly-create-and-run-concurrent-tasks-using-pythons-asyncio-module

if __name__=="__main__":
    if len(sys.argv) < 2:
        print("Arguments missing!")
        sys.exit()

    config_path = sys.argv[1]
    config = RCConfig(config_path)

    on_data = ext.load_modules(config, "on_data")
    on_save = ext.load_modules(config, "on_save")

    share = Queue()

    audio = RCAudio(config, share, on_data, on_save)
    server = RCWebSocket(config.get("server"), share)

    def t_audio():
        audio.run()

    def t_server():
        server.run()

    threads = [
        Thread(target=t_audio),
        Thread(target=t_server)
    ]

    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
