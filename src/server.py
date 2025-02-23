import sys
import signal
import json
import cv2 as cv
import numpy as np
import platform
import GPUtil

from cpuinfo import get_cpu_info
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

def worker_detect(config,device,yolo_path,yunet_path,stop_event):
    cap: RCVideoCapture = RCVideoCapture(device)
    yolo: RCYolo = RCYolo(yolo_path,config)
    yunet: RCYunet = RCYunet(yunet_path, config)

    sys_os = platform.freedesktop_os_release()
    sys_cpu = get_cpu_info()
    sys_gpus = GPUtil.getGPUs()

    def process(frame):
        b64_frame: str = b64encode(cv.imencode(".jpg", frame)[1]).decode()
        yolo_results: RCYoloResults = yolo.detect(frame)
        yunet_results: RCYunetResults = yunet.detect(frame)
        
        meta = {
            "system": {
                "sys": f'{sys_cpu["arch"]} {sys_os["PRETTY_NAME"]}',
                "cpu": sys_cpu["brand_raw"],
                "gpu": [n.name for n in sys_gpus],
                "gpuDriver": [n.driver for n in sys_gpus],
                "python": sys_cpu["python_version"],
                "opencv": cv.__version__,
                "fps": cap.fps,
                "captureDevice": device
            },
            "yolo": {
                "inputSize": yolo.config["img_size"],
                "chkpt": yolo.config["chkpt"].split("/")[-1]
            },
            "yunet": {
                "inputSize": yunet.config["img_size"],
                "chkpt": yunet.config["chkpt"].split("/")[-1]
            },
            "yoloInputSize": yolo.config["img_size"],
            "yunetInputSize": yunet.config["img_size"],
        }

        results = [yolo_results, yunet_results, meta]
        
        try:
            RCResultsQueue.put(results)
        except Full:
            logger("RCServer", "Results Queue is full!", level=LogLevel.WARNING)

        try:
            RCFramesQueue.put(b64_frame)
        except Full:
            logger("RCServer", "Frames Queue is full!", level=LogLevel.WARNING)

    cap.process(process, stop_event=stop_event)

def worker_socket(config,port,stop_event):
    # API socket connection
    api = APISocket(port=port)
    api.start_socket(results_queue=RCResultsQueue, frames_queue=RCFramesQueue, stop_event=stop_event)

if __name__=="__main__":
    if len(sys.argv) != 2:
        print("USAGE: $ server.py <config file>")
        exit(1)
   
    config_path = sys.argv[1]
    
    logger("RCServer", f"Loading config: {config_path}")
    with open(config_path) as f:
        config = json.load(f)

    # Capture device (dev or file)
    device: str = config["videoCapture"]["device"]
    logger("RCServer", f"Config :: Device: {device}")

    # YOLO path
    yolo_path: str = config["yolo"]["chkpt"]
    logger("RCServer", f"Config :: Yolo path: {yolo_path}")
    
    # Yunet path
    yunet_path: str = config["yunet"]["chkpt"]
    logger("RCServer", f"Config :: Yunet path: {yunet_path}")

    # API
    port: int = config["websocket"]["port"]
    logger("RCServer", f"Config :: Websocket port: {port}")
    
    # Create and start threads
    threads: list[Thread, Thread] = [
        Thread(target=worker_detect, args=(config, device, yolo_path, yunet_path, RCStopEvent)),
        Thread(target=worker_socket, args=(config, port, RCStopEvent))
    ]

    for t in threads:
        t.start()
   
    while threads[0].is_alive() or threads[1].is_alive():
        try:
            threads[0].join(1)
            threads[1].join(1)
        except KeyboardInterrupt as e:
            logger("RCServer", "Shutting down..")
            RCStopEvent.set()
            break

    RCStopEvent.set()
    threads[0].join()
    threads[1].join()
    logger("RCServer", "Goodbye!")
