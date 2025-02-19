from dataclasses import dataclass
from ultralytics import YOLO
from ultralytics.engine.results import Results
from box import RCBox
from utils.logger import logger

@dataclass
class RCDetectionResult:
    class_name: str
    confidence: str
    box: RCBox

class RCYoloResults:
    def __init__(self, raw: Results, names: list[str]):
        self.raw: Results = raw
        self.processed = self._process(raw, names)

    def _process(self, raw: Results, names: list[str]) -> list[RCDetectionResult]:
        r: list[RCDetectionResult] = []

        for n in raw:
            # Messy conversion, messy type annotation, sorry.
            classes: list[int] = [int(x) for x in n.boxes.cls.cpu().numpy()]
            confs: list[float] = [float(x) for x in n.boxes.conf.cpu().numpy()]
            boxes: list[list[int,int,int,int]] = n.boxes.xyxy.cpu().numpy()

            for _class, _conf, _box in zip(classes, confs, boxes):
                r.append(
                    RCDetectionResult(
                        class_name=names[_class],
                        confidence=_conf,
                        box=RCBox(
                            int(_box[0]),
                            int(_box[1]),
                            int(_box[2]),
                            int(_box[3])
                        )
                    )
                )
        
        return r 

class RCYunetResults:
    def __init__(self, raw: list[int, list]):
        self.raw: list[int, list] = raw
        self.processed: list[RCDetectionResult] = self._process(raw)

    def _process(self, raw: list[int, list]):
        r: list[RCDetectionResult] = []

        try:
            for n in raw[1]:
                r.append(
                    RCDetectionResult(
                        class_name="face",
                        confidence=float(n[-1]),
                        box=RCBox(
                            int(n[0]), 
                            int(n[1]), 
                            (int(n[0]) + int(n[2])),
                            (int(n[1]) + int(n[3])),
                        )
                    )
                )
        except TypeError:
            return r

        return r
