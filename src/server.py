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
from capture import RCVideoCapture, RCAudioCapture
from cap_yolo import RCYolo
from cap_yunet import RCYunet
from cap_whisper import RCWhisper
from api_socket import APISocket
from utils.logger import logger 
from result import RCYoloResults, RCYunetResults, RCWhisperResults

# https://docs.python.org/3/library/threading.html
# https://www.geeksforgeeks.org/multithreading-python-set-1/
# https://docs.python.org/3/library/queue.html#queue.SimpleQueue

# Data sharing between threads
RCVideoResultsQueue: Queue = Queue(maxsize=5)
RCAudioResultsQueue: Queue = Queue(maxsize=5)
RCFramesQueue: Queue = Queue(maxsize=5)

# Signaling
RCStopEvent: Event = Event()

def worker_audio(config,stop_event):
    cap: RCAudioCapture = RCAudioCapture(config)
    whisper = RCWhisper(config)

    def process(clip):
        results = whisper.detect(clip)

        try:
            RCAudioResultsQueue.put(results)
        except Full:
            logger("RCServer", "Audio Results Queue is full!", level=LogLevel.WARNING)

    cap.process(process, stop_event=stop_event)

def worker_video(config,device,yolo_path,yunet_path,stop_event):
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
            RCVideoResultsQueue.put(results)
        except Full:
            logger("RCServer", "Video Results Queue is full!", level=LogLevel.WARNING)

        try:
            RCFramesQueue.put(b64_frame)
        except Full:
            logger("RCServer", "Frames Queue is full!", level=LogLevel.WARNING)

    cap.process(process, stop_event=stop_event)

def worker_socket(config,port,stop_event):
    # API socket connection
    api = APISocket(port=port)
    api.start_socket(
        audio_results_queue=RCAudioResultsQueue,
        video_results_queue=RCVideoResultsQueue,
        frames_queue=RCFramesQueue,
        stop_event=stop_event
    )

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

    # YOLO path
    yolo_path: str = config["yolo"]["chkpt"]
    
    # Yunet path
    yunet_path: str = config["yunet"]["chkpt"]

    # API
    port: int = config["websocket"]["port"]
    
    # Create and start threads
    threads: list[Thread, Thread] = [
        Thread(target=worker_video, args=(config, device, yolo_path, yunet_path, RCStopEvent)),
        #Thread(target=worker_audio, args=(config, RCStopEvent)),
        Thread(target=worker_socket, args=(config, port, RCStopEvent))
    ]

    for t in threads:
        t.start()
   
    while not RCStopEvent.is_set():
        try:
            for t in threads:
                t.join(1)
        except KeyboardInterrupt as e:
            logger("RCServer", "Shutting down..")
            RCStopEvent.set()
            break

    logger("RCServer", "Goodbye!")
    RCStopEvent.set()

    for t in threads:
        t.join()
