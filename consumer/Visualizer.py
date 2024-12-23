from typing import Any
from Configuration import Configuration as CONFIG
import cv2
import numpy as np

class Visualizer():
    def __init__(self):
        pass
    
    @staticmethod
    def draw_sections(frame):
        for section_name in CONFIG.REGIONS_COORDS.keys():
            opacity=0.3
            overlay = frame.copy()
            points = np.array(CONFIG.REGIONS_COORDS[section_name], np.int32).reshape((-1, 1, 2))
            color = CONFIG.REGIONS_COLORS[section_name]
            cv2.fillPoly(overlay, [points], color)
            cv2.polylines(overlay, [points], isClosed=True, color=color, thickness=2)
            cv2.addWeighted(overlay, opacity, frame, 1 - opacity, 0, frame)
        return frame
    
    @staticmethod
    def draw_boxes(frame, prediction_results):
        boxes = prediction_results["boxes"]
        classes = prediction_results["classes"]
        ids = prediction_results["ids"]
        confs = prediction_results["confs"]
        
        for box, cls_, id_, conf in zip(boxes, classes, ids, confs):
            box = box.detach().to("cpu").numpy().astype(int).tolist()
            tlx, tly, brx, bry = box[0], box[1], box[2], box[3]

            if cls_ in CONFIG.VEHICLE_CLASSES:
                cv2.rectangle(frame, (tlx, tly), (brx, bry), CONFIG.CAR_BOX_COLOR, 2)
            elif cls_ in CONFIG.PERSON_CLASS:
                cv2.rectangle(frame, (tlx, tly), (brx, bry), CONFIG.PERSON_BOX_COLOR, 2)
        
        return frame