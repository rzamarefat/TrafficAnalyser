import cv2
from ultralytics import YOLO
from Configuration import Configuration as CONFIG
from Visualizer import Visualizer


class Analyser:
    def __init__(self):
        self._tracker_model = YOLO(CONFIG.TRACKER_CKPT_PATH)
        print("===> The tracker model is initialized...")

        self._visualizer_handler = Visualizer()

    
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


    def __call__(self, frame, frame_index):
        visualized_frame = frame.copy()
        
        prediction_results = self._track(frame)

        visualized_frame = self._visualizer_handler.draw_sections(visualized_frame)
        visualized_frame = self._visualizer_handler.draw_boxes(visualized_frame, prediction_results)

        cv2.imwrite(f"{frame_index}.png", visualized_frame)

if __name__ == "__main__":
    analyzer = Analyser()
    video_path = r"C:\Users\ASUS\Desktop\github_projects\traffic_analyser\videos\vlc-record-2024-12-22-18h18m06s-Screen_Recording_20241222_164344_YouTube.mp4-.mp4"
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

    