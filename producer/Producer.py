from RabbitHandler import RabbitHandler
from Configuration import Configuration as CONFIG
import cv2
from datetime import datetime
import base64

class Producer:
    def __init__(self):
        self._rabbit_publisher = RabbitHandler(CONFIG.QUEUE_NAME)
        self._rabbit_publisher.start()

        self.last_index = -1
    
    @staticmethod
    def _encode_img_to_base64(frame):
        _, buffer = cv2.imencode('.jpg', frame)
        image_bytes = buffer.tobytes()
        base64_encoded = base64.b64encode(image_bytes).decode('utf-8')

        return base64_encoded

    def __call__(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Erroor reading file")
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            margin = 150
            frame = frame[margin:1080-margin,:,:]
            
            timestamp = datetime.today().strftime('%Y-%m-%d')
            data_to_publish = {
                "img":self._encode_img_to_base64(frame),
                "metadata": f"{timestamp}__{self.last_index+1}"
            }
            
            self._rabbit_publisher.publish(data_to_publish)
            print("Published ...")

        cap.release()
        cv2.destroyAllWindows()