from RabbitPublisher import RabbitPublisher
from Configuration import Rabbit
import cv2
from datetime import datetime
import base64

class Producer:
    def __init__(self):
        self._rabbit_publisher = RabbitPublisher(Rabbit.QUEUE_NAME)
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
            
            timestamp = datetime.today().strftime('%Y-%m-%d')
            # if self.last_index == -1:
            #     self.last_index = self._db_handler.get_last_not_analyzed_index(timestamp=timestamp)
            #     if self.last_index is None:
            #         self.last_index = -1
            data_to_publish = {
                "img":self._encode_img_to_base64(frame),
                "metadata": f"{timestamp}__{self.last_index+1}"
            }
            
            self._rabbit_publisher.publish(data_to_publish)
            print("Published ...")
            # if self.last_index == -1:
            #     self._db_handler.push_frame_to_db(index=0, timestamp=timestamp)
            # else:
            #     self._db_handler.push_frame_to_db(index=self.last_index+1, timestamp=timestamp)
            # self.last_index = self.last_index + 1

        cap.release()
        cv2.destroyAllWindows()