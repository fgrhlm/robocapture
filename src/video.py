import logging
import ext

from worker import RCWorker
from cv2 import VideoCapture, CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT, CAP_PROP_POS_FRAMES, TickMeter
from queue import Queue

class RCVideo(RCWorker):
    def __init__(self, config, queue, on_data, on_save):
        RCWorker.__init__(self,"video",config, queue, on_data=on_data, on_save=on_save)
        self.timer = TickMeter()
        self.device = self.config.get("device")

        try:
            logging.debug(f"Opening VideoCapture: {self.device}")
            self.stream = VideoCapture(self.device)
            self.input_dims = {
                "w": int(self.stream.get(CAP_PROP_FRAME_WIDTH)),
                "h": int(self.stream.get(CAP_PROP_FRAME_HEIGHT))
            }
        except Exception as e:
            logging.error(f"Could not open VideoCapture! {e}")
            sys.exit()

    def run(self):
        logging.info("Starting RCVideo..")

        while True:
            if self.stop_signal:
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

            on_data_results = ext.run(self.on_data, frame)
            self.queue.put(on_data_results)

            self.timer.stop()
            self.fps = self.timer.getFPS()

        self.stream.release()
        logging.info("RCVideo stopped!")
