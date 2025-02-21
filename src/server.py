import sys
import signal
import json
import cv2 as cv
import numpy as np

from base64 import b64encode
from queue import Queue, Full
from threading import Event, Thread
from time import sleep
from capture import RCVideoCapture
from cap_yolo import RCYolo
from cap_yunet import RCYunet
from api_socket import APISocket
from utils.logger import logger 
from result import RCYoloResults, RCYunetResults

# https://docs.python.org/3/library/threading.html
# https://www.geeksforgeeks.org/multithreading-python-set-1/
# https://docs.python.org/3/library/queue.html#queue.SimpleQueue

# Data sharing between threads
RCResultsQueue: Queue = Queue(maxsize=5)
RCFramesQueue: Queue = Queue(maxsize=5)

# Signaling
RCStopEvent: Event = Event()

def worker_detect(yolo_path,yunet_path,stop_event):
    cap: RCVideoCapture = RCVideoCapture("media/test.mp4")
    yolo: RCYolo = RCYolo(yolo_path)
    yunet: RCYunet = RCYunet(yunet_path, (cap.frame_width, cap.frame_height))

    def process(frame):
        b64_frame: str = b64encode(cv.imencode(".jpg", frame)[1]).decode()
        yolo_results: RCYoloResults = yolo.detect(frame)
        yunet_results: RCYunetResults = yunet.detect(frame)

        results: list[RCYoloResults, RCYunetResults] = [yolo_results, yunet_results]
        
        try:
            RCResultsQueue.put(results)
        except Full:
            logger("RoboCaptureServer", "Results Queue is full!", level=LogLevel.WARNING)

        try:
            RCFramesQueue.put(b64_frame)
        except Full:
            logger("RoboCaptureServer", "Frames Queue is full!", level=LogLevel.WARNING)

    cap.process(process, stop_event=stop_event)

def worker_socket(port,stop_event):
    # API socket connection
    api = APISocket(port=port)
    api.start_socket(results_queue=RCResultsQueue, frames_queue=RCFramesQueue, stop_event=stop_event)

if __name__=="__main__":
    if len(sys.argv) != 4:
        print("USAGE: $ server.py <yolo_path> <yunet_path> <api port>")
        exit(1)
    
    # YOLO path
    yolo_path: str = sys.argv[1]
    
    # Yunet path
    yunet_path: str = sys.argv[2]

    # API
    port: int = int(sys.argv[3])
    
    # Create and start threads
    threads: list[Thread, Thread] = [
        Thread(target=worker_detect, args=(yolo_path, yunet_path,RCStopEvent)),
        Thread(target=worker_socket, args=(port,RCStopEvent))
    ]

    for t in threads:
        t.start()
   
    while threads[0].is_alive() or threads[1].is_alive():
        try:
            threads[0].join(1)
            threads[1].join(1)
        except KeyboardInterrupt as e:
            logger("RoboCaptureServer", "Shutting down..")
            RCStopEvent.set()
            break

    RCStopEvent.set()
    threads[0].join()
    threads[1].join()
    logger("RoboCaptureServer", "Goodbye!")
