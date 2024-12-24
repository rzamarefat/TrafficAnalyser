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
    def draw_compass(frame):
        height, width, _ = frame.shape
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2
        color = CONFIG.COMPASS_COLOR
        thickness = 2
        text_color = (255, 255, 255)  # White color for text
        background_color = (0, 0, 0)  # Black background

        mid_x = width // 2
        mid_y = height // 2

        # Draw "N" with black background
        text = 'N'
        (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
        text_x = mid_x - 10
        text_y = 50
        cv2.rectangle(frame, (text_x - 5, text_y - text_height - 5), (text_x + text_width + 5, text_y + 5), background_color, -1)
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, text_color, thickness)

        # Draw "S" with black background
        text = 'S'
        (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
        text_x = mid_x - 10
        text_y = height - 30
        cv2.rectangle(frame, (text_x - 5, text_y - text_height - 5), (text_x + text_width + 5, text_y + 5), background_color, -1)
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, text_color, thickness)

        # Draw "E" with black background
        text = 'E'
        (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
        text_x = width - 60
        text_y = mid_y
        cv2.rectangle(frame, (text_x - 20, text_y - text_height // 2 - 30), (text_x + text_width, text_y + text_height // 2), background_color, -1)
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, text_color, thickness)

        # Draw "W" with black background
        text = 'W'
        (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
        text_x = 10
        text_y = mid_y
        cv2.rectangle(frame, (text_x - 5, text_y - text_height // 2 - 30), (text_x + text_width, text_y + text_height // 2), background_color, -1)
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, text_color, thickness)

        return frame
    
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