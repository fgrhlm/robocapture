from dataclasses import dataclass

@dataclass
class RCBox:
    """Detection result box coordinates (top-left and bottom-right)"""
    x1: int
    y1: int
    x2: int
    y2: int
