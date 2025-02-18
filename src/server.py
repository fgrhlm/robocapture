import sys
import threading
import queue
import signal
import json

from time import sleep
from capture import RCVideoCapture
from cap_yolo import RCYolo
from cap_yunet import RCYunet
from api_socket import APISocket
from utils.logger import logger 

# https://docs.python.org/3/library/threading.html
# https://www.geeksforgeeks.org/multithreading-python-set-1/
# https://docs.python.org/3/library/queue.html#queue.SimpleQueue

# Data sharing between threads
RCResultsQueue = queue.SimpleQueue()

# Signaling
RCStopEvent = threading.Event()

def worker_detect(yolo_path,yunet_path):
    cap = RCVideoCapture("media/test.mp4")
    yolo = RCYolo(yolo_path)
    yunet = RCYunet(yunet_path, (cap.frame_width, cap.frame_height))

    def process(frame):
        yolo_results = yolo.detect(frame)
        yunet_results = yunet.detect(frame)

        results = {
            "yolo": yolo_results,
            "yunet": yunet_results
        }
        
        try:
            RCResultsQueue.put(results)
        except queue.Full:
            logger("RoboCaptureServer", "Queue is full!", level=LogLevel.WARNING)

    cap.process(process, stop_event=RCStopEvent)

def worker_socket(port):
    # API socket connection
    api = APISocket(port=port)
    api.listen(results_queue=RCResultsQueue, stop_event=RCStopEvent)

if __name__=="__main__":
    if len(sys.argv) != 4:
        print("USAGE: $ server.py <yolo_path> <yunet_path> <api port>")
        exit(1)
    
    # YOLO path
    yolo_path = sys.argv[1]
    
    # Yunet path
    yunet_path = sys.argv[2]

    # API
    port = int(sys.argv[3])
    
    # Create and start threads
    threads = [
        threading.Thread(target=worker_detect, args=(yolo_path, yunet_path,)),
        threading.Thread(target=worker_socket, args=(port,))
    ]

    for t in threads:
        t.start()

    try:
        while threads[0].is_alive() and threads[1].is_alive():
            sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger("RoboCaptureServer", "Shutting down..")
        RCStopEvent.set()

    for t in threads:
        t.join()

    logger("RoboCaptureServer", "Goodbye!")
    exit(0)

