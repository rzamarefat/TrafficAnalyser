import cv2
from ultralytics import YOLO
from Configuration import Configuration as CONFIG
from Visualizer import Visualizer
import torch

class Analyser:
    def __init__(self):
        self._tracker_model = YOLO(CONFIG.TRACKER_CKPT_PATH)
        print("===> The tracker model is initialized...")

        self._visualizer_handler = Visualizer()
        self._history_holder = {
            "prediction_results": None
        }

    
    def _track(self, frame):
        results = self._tracker_model.track(frame, persist=True,device=CONFIG.DEVICE,tracker="bytetrack.yaml" ,conf=CONFIG.TRACKER_CONFIDENCE, iou=CONFIG.TRACKER_IOU, verbose=False, imgsz=CONFIG.MODEL_IMGSZ)

        boxes = results[0].boxes.xyxy.to(CONFIG.DEVICE)
        confs = results[0].boxes.conf.cpu().numpy()
        classes = results[0].boxes.cls.cpu().numpy().astype(int)

        if results[0].boxes.id is None:
            ids = [None for _ in range(len(boxes))]
        else:
            ids = results[0].boxes.id.cpu().numpy().astype(int)

        return {
            "boxes": boxes,
            "classes": classes,
            "ids": ids,
            "confs": confs
        }
        

    def _get_cars_direction(self, curr_boxes, last_boxes, ids, prev_ids):
        ids = torch.tensor(ids, device=CONFIG.DEVICE)
        prev_ids = torch.tensor(prev_ids, device=CONFIG.DEVICE)

        mutual_ids = torch.tensor(list(set(ids.tolist()) & set(prev_ids.tolist())), device=CONFIG.DEVICE)
        curr_idx = torch.nonzero(torch.isin(ids, mutual_ids)).squeeze(1)
        prev_idx = torch.nonzero(torch.isin(prev_ids, mutual_ids)).squeeze(1)

        curr_boxes = curr_boxes[curr_idx]
        last_boxes = last_boxes[prev_idx]

        curr_centers = (curr_boxes[:, :2] + curr_boxes[:, 2:]) / 2  # (N, 2)
        last_centers = (last_boxes[:, :2] + last_boxes[:, 2:]) / 2  # (N, 2)

        diffs = curr_centers - last_centers  # (N, 2)

        directions = ["" for _ in range(len(diffs))]
        
        for i, diff in enumerate(diffs):
            print(diff)
            if diff[0] > 0 and diff[1] > 0:
                directions[i] = "S"  # x increasing, y increasing
            elif diff[0] < 0 and diff[1] < 0:
                directions[i] = "N"  # x decreasing, y decreasing
            elif diff[0] > 0 and diff[1] < 0:
                directions[i] = "E"  # x increasing, y decreasing
            elif diff[0] < 0 and diff[1] > 0:
                directions[i] = "W"  # x decreasing, y increasing

        movement_dict = {id_.item(): direction for id_, direction in zip(mutual_ids, directions)}

        return movement_dict
       



    def __call__(self, frame, frame_index):
        visualized_frame = frame.copy()
        
        prediction_results = self._track(frame)
        if self._history_holder["prediction_results"] is not None:
            direction_results = self._get_cars_direction(prediction_results["boxes"], 
                                                         self._history_holder["prediction_results"]["boxes"], 
                                                         prediction_results["ids"], 
                                                         self._history_holder["prediction_results"]["ids"])
        else:
            direction_results = {}
            
        self._history_holder["prediction_results"] = prediction_results

        visualized_frame = self._visualizer_handler.draw_sections(visualized_frame)
        visualized_frame = self._visualizer_handler.draw_boxes(visualized_frame, prediction_results, direction_results)
        visualized_frame = self._visualizer_handler.draw_compass(visualized_frame)

        

        cv2.imwrite(f"{frame_index}.png", visualized_frame)

if __name__ == "__main__":
    analyzer = Analyser()
    video_path = r"C:\Users\ASUS\Desktop\github_projects\traffic_analyser\videos\01.mp4"
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Unable to open video file: {video_path}")

    frame_count = 0

    while True:
        # Read the next frame
        ret, frame = cap.read()
        margin = 150
        frame = frame[margin:1080-margin,:,:]

        if not ret:
            break

        analyzer(frame, frame_count)

        frame_count += 1

    cap.release()
    print("Frame extraction completed.")

    