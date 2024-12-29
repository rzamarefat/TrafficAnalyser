from typing import Any
from Configuration import Configuration as CONFIG
import cv2
import os
import json
import numpy as np

class ColorPallete:
    ZONES = {
            'z1': (255, 131, 67),
            'z12': (234, 56, 78),
            'z2': (23, 155, 174),
            'z3': (65, 88, 166),
            'z4': (239, 90, 111),
            'z5': (212, 189, 172),
            'z6': (67, 89, 23),
            'z7': (123, 234, 45),
            'z8': (0, 123, 255),
            'z9': (123, 0, 255),
            'z14': (89, 67, 45),
            'z11': (255, 123, 0),
            'z10': (12, 255, 78),
            'z13': (34, 56, 78),
            'pz2': (200, 200, 0),
            'pz1': (159, 159, 159),
            'zz': (255, 2, 255),
            "nothing": (0,0,0)
        }

class Visualizer():
    def __init__(self):
        self._parse_scene_composition()

    @staticmethod
    def _get_top_bottom_points(coordinates):
        p1, p2 = coordinates
        x1, y1 = p1
        x2, y2 = p2
        if x1 > x2 and y1 < y2:
            adjusted_rectangle = [[x2, y1], [x1, y2]]
        elif x1 < x2 and y1 < y2:
            adjusted_rectangle = coordinates
        elif x1 > x2 and y1>y2:
            adjusted_rectangle = [[x2, y2], [x1, y1]]
        
        return adjusted_rectangle
    
    
    def _parse_scene_composition(self):
        path_to_config = os.path.join(os.getcwd(), "scene_composition.json")
        with open(path_to_config, 'r') as file:
            info = json.load(file)
        

        self._img_height = info["imageHeight"]
        self._img_width = info["imageWidth"]

        self._zones = {shape["label"]:self._get_top_bottom_points(shape["points"])  for shape in info["shapes"] if shape["label"].__contains__("z")}
        self._car_cells = [self._get_top_bottom_points(shape["points"])  for shape in info["shapes"] if shape["label"] == "car_cell"]
    
    def draw_cells(self, frame, filled_cells_indixes):
        overlay = frame.copy()
    
        for index, rect in enumerate(self._car_cells):
            top_left = (int(rect[0][0]), int(rect[0][1]))
            bottom_right = (int(rect[1][0]), int(rect[1][1]))
            if index in filled_cells_indixes:
                color = (0, 0, 255)
            else:
                color = (0, 255, 0)

            cv2.rectangle(overlay, top_left, bottom_right, color, -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.8, 0, frame)
        
        return frame

    def draw_zones(self, frame):
        for k, v in self._zones.items():
            opacity=0.2
            overlay = frame.copy()
            points = np.array(v, np.int32).reshape((-1, 1, 2))
            cv2.fillPoly(overlay, [points], ColorPallete.ZONES[k])
            cv2.polylines(overlay, [points], isClosed=True, color=ColorPallete.ZONES[k], thickness=2)
            cv2.addWeighted(overlay, opacity, frame, 1 - opacity, 0, frame)

        return overlay
        
    
    @staticmethod
    def draw_boxes(frame, prediction_results, direction_results):
        boxes = prediction_results["boxes"]
        classes = prediction_results["classes"]
        ids = prediction_results["ids"]
        confs = prediction_results["confs"]
        
        for box, cls_, id_, conf in zip(boxes, classes, ids, confs):
            box = box.detach().to("cpu").numpy().astype(int).tolist()
            tlx, tly, brx, bry = box[0], box[1], box[2], box[3]

            if cls_ in CONFIG.VEHICLE_CLASSES:
                cv2.rectangle(frame, (tlx, tly), (brx, bry), CONFIG.CAR_BOX_COLOR, 2)
                if id_ in direction_results.keys():
                    cv2.putText(frame, direction_results[id_], (int((tlx+brx)/2), int((tly+bry)/2)), cv2.FONT_HERSHEY_SIMPLEX, 1, CONFIG.CAR_BOX_COLOR, 2)
            elif cls_ in CONFIG.PERSON_CLASS:
                cv2.rectangle(frame, (tlx, tly), (brx, bry), CONFIG.PERSON_BOX_COLOR, 2)
        
        return frame