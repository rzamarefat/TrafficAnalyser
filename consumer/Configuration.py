import os
import torch

root = os.getcwd()

class Configuration:
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

    # Tracker
    TRACKER_NAME = "botsort.yaml"
    TRACKER_CONFIDENCE = 0.5
    TRACKER_IOU = 0.5
    MODEL_IMGSZ = 960
    TRACKER_CKPT_PATH = os.path.join(root, "weights", "yolo11l.pt")

    # Rabbit
    RABBIT_CREDENTIALS_USERNAME = "guest"
    RABBIT_CREDENTIALS_PASSWORD = "guest"
    RABBIT_IP = "127.0.0.1"
    CONSUMER_QUEUE_NAME = "traffic-consumer"
    PRODUCER_QUEUE_NAME = "traffic-producer"

    
    VEHICLE_CLASSES = [1, 2, 3, 5, 7]
    PERSON_CLASS = [0]


    #Visualization
    CAR_BOX_COLOR  = (0, 160, 110)
    PERSON_BOX_COLOR = (90, 90, 255)

    COMPASS_COLOR = (255, 119, 20)
    
    REGIONS_COORDS = {
        "cross": [[369.,485],[499,701],[1440,599],[1115,430]],
        "r1": [[4,588],[406,544],[479,673],[7,734]],
        "r2": [[371,491],[405,543],[0,583],[2,529]],
        "r3": [[815,435],[214,25],[149,22],[433,472]],
        "r4": [[216,22],[817,436],[1048,427],[268,23]],
        "r5": [[1218,477],[1725,437],[1727,390],[1115,430]],
        "r6": [[1221,477],[1420,582],[1729,529],[1729,441]],
        "r7": [[1406,607],[972,648],[1121,777],[1713,770]],
        "r8": [[968,648],[1119,779],[651,779],[602,696]],
    }

    REGIONS_COLORS = {
        "cross": (255, 120, 250),
        "r1": (250, 180, 50),
        "r2": (50, 255, 20),
        "r3": (255, 190, 50),
        "r4": (50, 190, 250),
        "r5": (255, 255, 110),
        "r6": (78, 78, 110),
        "r7": (169, 65, 150),
        "r8": (20, 120, 150),
    }