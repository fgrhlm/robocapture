import sys
import threading
import queue
import signal

from time import sleep
from cap_yolo import YOLOCapture
from api_socket import APISocket
from utils.logger import logger 

# https://docs.python.org/3/library/threading.html
# https://www.geeksforgeeks.org/multithreading-python-set-1/
# https://docs.python.org/3/library/queue.html#queue.SimpleQueue

YOLOQueue = queue.SimpleQueue()
YOLOStopEvent = threading.Event()

def job_cap(yolo_path):
    yolo = YOLOCapture(yolo_path, "media/test.mp4")
    yolo.run(_queue=YOLOQueue)

def job_api(port):
    # API socket connection
    api = APISocket(port=port)
    api.listen(_queue=YOLOQueue)

if __name__=="__main__":
    if len(sys.argv) != 3:
        print("USAGE: $ yolo_demo.py <yolo_path> <api port>")
        exit(1)
    
    # YOLO
    yolo_path = sys.argv[1]

    # API
    port = int(sys.argv[2])
    
    # Create and start threads
    threads = [
        threading.Thread(target=job_cap, args=(yolo_path,)),
        threading.Thread(target=job_api, args=(port,))
    ]

    for t in threads:
        t.start()

    try:
        while threads[0].is_alive() and threads[1].is_alive():
            sleep(1)
    except KeyboardInterrupt:
        logger("YOLODemo", "<CTRL-C> User requested termination!")

    for t in threads:
        t.join()

    logger("YOLODemo", "Goodbye!")
    exit(0)

