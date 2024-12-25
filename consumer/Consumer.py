from Analyzer import Analyser
import pika
from Configuration import Configuration as CONFIG
import numpy as np
import cv2
import base64
import json
import msgpack
import time
import traceback
from ultralytics import YOLO

class Consumer:
    def __init__(self):
        self._tracker_handler = Analyser()
        
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(host="127.0.0.1"))
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue=CONFIG.PRODUCER_QUEUE_NAME)

    @staticmethod
    def _convert_image_to_bytes(frame):
        ret, buffer = cv2.imencode('.jpg', frame)
        image_bytes = buffer.tobytes()
        return image_bytes
    
    @staticmethod
    def convert_numpy_to_python(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.integer, int)):
            return int(obj)
        elif isinstance(obj, (np.floating, float)):
            return float(obj)
        elif isinstance(obj, tuple):
            return tuple(Consumer.convert_numpy_to_python(item) for item in obj)
        elif isinstance(obj, list):
            return [Consumer.convert_numpy_to_python(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: Consumer.convert_numpy_to_python(value) for key, value in obj.items()}
        else:
            return obj

    @staticmethod
    def _encode_img_to_base64(frame):
        _, buffer = cv2.imencode('.jpg', frame)
        image_bytes = buffer.tobytes()
        base64_encoded = base64.b64encode(image_bytes).decode('utf-8')

        return base64_encoded


    def _publish_image_with_metadata(self, frame, metadata):
        # image_bytes = self._convert_image_to_bytes(frame)

        payload = {
            'img': self._encode_img_to_base64(frame),
            'metadata': "Consumer.convert_numpy_to_python(metadata)"
        }
    
        payload_json = msgpack.packb(payload, use_bin_type=True)

        credentials = pika.PlainCredentials(CONFIG.RABBIT_CREDENTIALS_USERNAME, CONFIG.RABBIT_CREDENTIALS_PASSWORD)
        parameters = pika.ConnectionParameters(
            host=CONFIG.RABBIT_HOST,
            port=CONFIG.RABBIT_PORT,
            virtual_host="/",
            credentials=credentials
        )

        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.queue_declare(queue=CONFIG.CONSUMER_QUEUE_NAME)

        channel.basic_publish(exchange='', routing_key=CONFIG.CONSUMER_QUEUE_NAME, body=payload_json)
        connection.close()

    @staticmethod
    def _convert_bytes_to_image(image_bytes):
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return frame
    
    @staticmethod
    def _convert_base64_to_img(base64_img):
        return base64.b64decode(base64_img)
        
    def __call__(self, frame=None):
        while True:
            def callback(ch, method, properties, body):
                # try:
                    tic = time.time()
                    fetched_data = json.loads(body.decode('utf-8'))
                    frame = base64.b64decode(fetched_data['img'])
                    frame = np.frombuffer(frame, dtype=np.uint8)
                    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
                    
                    print("frame decoded time:" , time.time() - tic)

                    metadata = fetched_data['metadata']
                    timestamp = metadata.split("__")[0]
                    index = int(metadata.split("__")[1])

                    visualized_frame, consumed_metadata = self._tracker_handler(frame, index)
                    self._publish_image_with_metadata(visualized_frame, consumed_metadata)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    
                    
                # except Exception as e:
                #     print(f"ERROR:\n{str(traceback.format_exc())}\n")
                #     ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

            self._channel.basic_qos(prefetch_count=1)
            self._channel.basic_consume(queue=CONFIG.PRODUCER_QUEUE_NAME, on_message_callback=callback, auto_ack=False)
            self._channel.start_consuming()
