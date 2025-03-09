import logging

from cv2 import VideoCapture, CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT, CAP_PROP_POS_FRAMES, TickMeter
from threads import RCThread
from pipeline import RCPipeline
from worker import RCWorker
from queue import Full, Empty, Queue

class RCVideo(RCWorker):
    def __init__(self, config, stop_event, data_queue):
        RCWorker.__init__(self, config, stop_event, data_queue)
        
        self.timer = TickMeter()
        self.device = self.config["device"]
        
        try:
            logging.debug("Opening VideoCapture..")
            self.stream = VideoCapture(self.device)
            self.input_dims = {
                "w": int(self.stream.get(CAP_PROP_FRAME_WIDTH)),
                "h": int(self.stream.get(CAP_PROP_FRAME_HEIGHT))
            }
        except Exception as e:
            logging.error(f"Could not open VideoCapture! {e}")
            self.stop_event.set()


    def run(self):
        logging.info("Starting RCVideo..")

        while True:
            if self.stop_event and self.stop_event.is_set():
                break

            if not self.stream.isOpened():
                break
            
            self.timer.start()
            ret, frame = self.stream.read()

            # DEBUG DEBUG DEBUG
            if not ret:
                self.stream.set(CAP_PROP_POS_FRAMES, 0)
                continue
            # DEBUG DEBUG DEBUG

            results = self.pipeline.exec("on_data", frame)

            try:
                self.queue.put(results)
            except Full:
                logging.debug("Video out queue full!")

            self.timer.stop()
            self.fps = self.timer.getFPS()
        
        self.stream.release()
        self.stop_event.set()
        logging.info("Stopping RCVideo..")

class RCVideoThread(RCThread):
    def __init__(self, config, stop_event, data_queue):
        RCThread.__init__(self, "t_video", config, stop_event, data_queue)

    def run(self):
        video = RCVideo(self.config, self.stop_event, self.queue) 
        
        self.set_ready(True)
        video.run()
