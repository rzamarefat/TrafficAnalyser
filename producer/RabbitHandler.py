import threading
from time import sleep
from pika import ConnectionParameters, BlockingConnection, PlainCredentials
from Configuration import Configuration as CONFIG
import json

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