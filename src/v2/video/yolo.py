import logging
import sys
import cv2 as cv
import numpy as np
import queue
import json

from pipeline import RCPipelineResult
from ultralytics import YOLO
from ultralytics.engine.results import Results

class RCYolo:
    def __init__(self, config):
        self.name = "yolo"
        self.config = config["ext"]["yolo"]

        try:
            self.yolo = YOLO(
                self.config["checkpoint"],
                task="detect",
                verbose=self.config["verbose"]
            )
        except Exception as e:
            logging.error(f"Cant load YOLO: {e}")
            raise Exception("Failed to load yolo!")

        if self.config["cpu"]:
            self.yolo = self.yolo.to("cpu")

    def process(self, frame):
        f = cv.resize(frame, (640, 640)) 

        results = self.yolo(
            f,
            verbose=self.config["verbose"],
            stream=self.config["stream"],
            conf=self.config["min_conf"],
            half=self.config["fp16"],
            max_det=self.config["max_detect"],
            vid_stride=self.config["vid_stride"]
        )
       
        results = RCPipelineResult("yolo", results)
        
        return results

step = RCYolo
