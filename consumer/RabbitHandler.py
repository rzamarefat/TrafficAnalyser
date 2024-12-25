import threading
import msgpack
from time import sleep
from pika import ConnectionParameters, BlockingConnection, PlainCredentials
from Configuration import Configuration as CONFIG
import json
import cv2
import base64

class RabbitHandler(threading.Thread):
    def __init__(self, queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daemon = True
        self.is_running = True
        self.queue = queue

        credentials = PlainCredentials(CONFIG.RABBIT_CREDENTIALS_USERNAME, CONFIG.RABBIT_CREDENTIALS_PASSWORD)
        parameters = ConnectionParameters(CONFIG.RABBIT_IP, credentials=credentials)
        self.connection = BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue)

    def run(self):
        while self.is_running:
            self.connection.process_data_events(time_limit=1)

    def _publish(self, message):
        self.channel.basic_publish("", self.queue, body=message)
        
    def _publish_image_with_metadata(self, frame, metadata):
        print("metadata", metadata)
        payload = {
            'img': self._encode_img_to_base64(frame),
            'metadata': f"meta"
        }
    
        payload = json.dumps(payload).encode('utf-8')

        credentials = PlainCredentials(CONFIG.RABBIT_CREDENTIALS_USERNAME, CONFIG.RABBIT_CREDENTIALS_PASSWORD)
        parameters = ConnectionParameters(
            host=CONFIG.RABBIT_HOST,
            port=CONFIG.RABBIT_PORT,
            virtual_host="/",
            credentials=credentials
        )

        connection = BlockingConnection(parameters)
        channel = connection.channel()

        channel.queue_declare(queue=CONFIG.CONSUMER_QUEUE_NAME)

        channel.basic_publish(exchange='', routing_key=CONFIG.CONSUMER_QUEUE_NAME, body=payload)
        connection.close()

    def publish(self, message):
        message = json.dumps(message).encode('utf-8')
        self.connection.add_callback_threadsafe(lambda: self._publish(message))

    def stop(self):
        print("Stopping...")
        self.is_running = False
        self.connection.process_data_events(time_limit=1)
        if self.connection.is_open:
            self.connection.close()
        print("Stopped")
        
    def consume(self, queue, on_message_callback):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=queue, on_message_callback=on_message_callback, auto_ack=False)
        self.channel.start_consuming()
        
    @staticmethod
    def _encode_img_to_base64(frame):
        _, buffer = cv2.imencode('.jpg', frame)
        image_bytes = buffer.tobytes()
        base64_encoded = base64.b64encode(image_bytes).decode('utf-8')

        return base64_encoded