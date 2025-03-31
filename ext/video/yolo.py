import os
import logging
import sys
import cv2 as cv
import numpy as np
import queue
import json
import enum

from ultralytics import YOLO
from ultralytics.engine.results import Results
from dataclasses import dataclass

from src.ext import RCExtWorker

# https://docs.opencv.org/4.x/d0/dd4/tutorial_dnn_face.html
# https://docs.ultralytics.com/modes/predict/
# https://www.geeksforgeeks.org/object-detection-with-yolo-and-opencv/
# https://github.com/ultralytics/ultralytics/blob/main/docs/en/usage/simple-utilities.md
# https://docs.ultralytics.com/modes/predict/#inference-arguments

class RCYoloLoader():
    def __init__(self, config):
        self.config = config
        self.verbose = self.config["verbose"]
        self.format = self.config["model_format"]
        self.weights = self.config["weights"]

        if self.format != "pytorch":
            self.export_config = self.config["export_config"][self.format]
            logging.debug(f"Config ({format}): {self.export_config}")

    def load(self):
        fn = self.weights
        format = self.format
        model = YOLO(fn, verbose=self.verbose)

        logging.debug(f"Initializing YOLO ({fn}) [{format}]")

        match format:
            case "pytorch":
                out = fn
            case "onnx":
                out = f"{fn.split(".")[0]}.onnx"
                logging.debug(f"Exporting model (pytorch -> {format})..")
                if not out in os.listdir("res/"):
                    out = model.export(
                        format=format,
                        imgsz=(self.config["img_size"][0], self.config["img_size"][0]),
                        half=self.export_config["half"],
                        simplify=self.export_config["simplify"],
                        nms=self.export_config["nms"],
                    )

                logging.debug(f"Export done! {out}")
            case "openvino":
                out = f"{fn.split("/")[-1].split(".")[0]}_openvino_model/"
                logging.debug(f"Exporting model (pytorch -> {format})..")
                if not out in os.listdir("res/"):
                    out = model.export(
                        format=format,
                        imgsz=(self.config["img_size"][0], self.config["img_size"][0]),
                        half=self.export_config["half"],
                        int8=self.export_config["int8"],
                        nms=self.export_config["nms"],
                    )

                logging.debug(f"Export done! {out}")
            case "tensor_rt":
                out = f"{fn.split("/")[-1].split(".")[0]}.engine"
                logging.debug(f"Exporting model (pytorch -> {format})..")
                if not out in os.listdir("res/"):
                    out = model.export(
                        format="engine",
                        imgsz=(self.config["img_size"][0], self.config["img_size"][0]),
                        half=self.export_config["half"],
                        simplify=self.export_config["simplify"],
                        nms=self.export_config["nms"],
                        int8=self.export_config["int8"],
                    )

                logging.debug(f"Export done! {out}")
            case "tflite":
                out = f"{fn.split("/")[-1].split(".")[0]}.tflite"
                logging.debug(f"Exporting model (pytorch -> {format})..")
                if not out in os.listdir("res/"):
                    out = model.export(
                        format=format,
                        imgsz=(self.config["img_size"][0], self.config["img_size"][0]),
                        half=self.export_config["half"],
                        int8=self.export_config["int8"],
                        nms=self.export_config["nms"],
                    )

                logging.debug(f"Export done! {out}")
            case _:
                raise Exception(f"Unknown format: {format}")

        logging.debug(f"Loading YOLO: {out}..")
        model = YOLO(
            out,
            verbose=self.verbose,
            task="detect"
        )

        return model

class RCYolo(RCExtWorker):
    def __init__(self, config):
        RCExtWorker.__init__(self, "yolo", config)
        self.loader = RCYoloLoader(config)
        self.yolo = self.loader.load()

    def process(self, frame):
        f = cv.resize(frame, (self.config["img_size"][0],self.config["img_size"][1]))

        raw_results: Results = self.yolo(
            f,
            verbose=self.config["verbose"],
            stream=self.config["stream"],
            conf=self.config["min_conf"],
            half=self.config["half"],
            max_det=self.config["max_detect"],
            vid_stride=self.config["vid_stride"]
        )

        results = []
        for n in raw_results:
            classes = [int(x) for x in n.boxes.cls.cpu().numpy()]
            confs = [float(x) for x in n.boxes.conf.cpu().numpy()]
            boxes = n.boxes.xywh.cpu().numpy()

            for _class, _conf, _box in zip(classes, confs, boxes):
                results.append({
                    "class": self.yolo.names[_class],
                    "conf": _conf,
                    "box": {
                        "x": int(_box[0]),
                        "y": int(_box[1]),
                        "w": int(_box[2]),
                        "h": int(_box[3])
                    }
                })

        return {
            "name": "yolo",
            "data": results
        }

ext = RCYolo
