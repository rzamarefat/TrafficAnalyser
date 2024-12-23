import os
import torch

root = os.getcwd()

class Configuration:
    TRACKER_CKPT_PATH = os.path.join(root, "weights", "yolo11l.pt")
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

    TRACKER_NAME = "botsort.yaml"
    TRACKER_CONFIDENCE = 0.5
    TRACKER_IOU = 0.5
    MODEL_IMGSZ = 960