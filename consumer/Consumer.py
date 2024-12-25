from typing import Any
from Analyzer import Analyser
import pika
from Configuration import Configuration as CONFIG
import numpy as np
import cv2
import base64
import json
import time
import traceback
from RabbitHandler import RabbitHandler

class Consumer:
    def __init__(self):
        self._analyser = Analyser()
        self._rabbit_handler = RabbitHandler(CONFIG.PRODUCER_QUEUE_NAME)

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
                    
                    
                    visualized_frame, meta = self._analyser(frame, index)

                    self._rabbit_handler._publish_image_with_metadata(visualized_frame, meta)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    
                    # if index == 0:
                    #     frame, meta, info = self._analyser.track(frame, track_model_results=track_model_results)
    
                    #     self._publish_image_with_metadata(frame, meta)
                    #     self._database_handler.update_frame_stats(index=index, timestamp=timestamp, stat=info, meta=meta)
                    #     ch.basic_ack(delivery_tag=method.delivery_tag)
                    # else:
                    #     prev_info = self._database_handler.get_frame_info(index=index - 1, timestamp=timestamp)
                    #     is_prev_frame_analyzed = prev_info != None
                    #     prev_frame_found = is_prev_frame_analyzed
                        
                    #     if is_prev_frame_analyzed:
                    #         frame, meta, info = self._analyser.track(frame, track_model_results=track_model_results, info=prev_info)
                    #         self._rabbit_handler._publish_image_with_metadata(frame, meta)
                    #         self._database_handler.update_frame_stats(index=index, timestamp=timestamp, stat=info, meta=meta)
                    #     else:
                    #         retry_counter = time.time()
                    #         while not(prev_frame_found):
                    #             if time.time() - retry_counter > 2:
                    #                 print(f'retrying in {int(CONFIG.General.SECONDS_WAIT_BEFORE_RETRY - (time.time() - retry_counter)) + 1}')
                    #                 time.sleep(1)
                    #             if time.time() - retry_counter > CONFIG.General.SECONDS_WAIT_BEFORE_RETRY:
                    #                 ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                    #                 return
                    #             is_prev_frame_analyzed = self._database_handler.get_frame_info(index=index - 1, timestamp=timestamp)
                    #             if is_prev_frame_analyzed:
                    #                 prev_frame_found = True
                                    
                    #                 frame, meta, info = self._analyser.track(frame,track_model_results=track_model_results, info=prev_info)
                    #                 self._rabbit_handler._publish_image_with_metadata(frame, meta)
                    #                 self._database_handler.update_frame_stats(index=index, timestamp=timestamp, stat=info, meta=meta)
                    #     ch.basic_ack(delivery_tag=method.delivery_tag)

                    print("=================")
                    print("publish time:" , time.time() - tic)
                # except Exception as e:
                #     print(f"ERROR:\n{str(traceback.format_exc())}\n")
                #     ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

            self._rabbit_handler.consume(queue=CONFIG.PRODUCER_QUEUE_NAME, on_message_callback=callback)