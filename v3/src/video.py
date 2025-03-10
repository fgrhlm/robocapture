import logging

from cv2 import VideoCapture, CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT, CAP_PROP_POS_FRAMES, TickMeter
from asyncio import Queue

class RCVideo:
    def __init__(self, config, shared_queue):
        
        self.timer = TickMeter()
        self.device = self.config["device"]
        self.shared_queue = shared_queue
        
        try:
            logging.debug("Opening VideoCapture..")
            self.stream = VideoCapture(self.device)
            self.input_dims = {
                "w": int(self.stream.get(CAP_PROP_FRAME_WIDTH)),
                "h": int(self.stream.get(CAP_PROP_FRAME_HEIGHT))
            }
        except Exception as e:
            logging.error(f"Could not open VideoCapture! {e}")
            sys.exit()

    async def run(self, ext_on_data):
        logging.info("Starting RCVideo..")

        while True:
            if not self.stream.isOpened():
                break
            
            self.timer.start()
            ret, frame = self.stream.read()

            # DEBUG DEBUG DEBUG
            if not ret:
                self.stream.set(CAP_PROP_POS_FRAMES, 0)
                continue
            # DEBUG DEBUG DEBUG

            on_data_results = ext_on_data(frame)
            self.shared_queue.put(on_data_results)

            self.timer.stop()
            self.fps = self.timer.getFPS()
        
        self.stream.release()
        logging.info("Stopping RCVideo..")
