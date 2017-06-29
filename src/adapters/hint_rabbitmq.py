import json

import pika

from adapters.abstract_adapter import AbstractAdapter
from utils.time_utils import TimeUtils


class HINTRabbitMQ(AbstractAdapter):
    """
    A custom adapter for the HINT network emulator
    Options of the form: antoine_node.6.buffer (i.e., the RabbitMQ queue to consume)
    """

    URL_BASE_RABBITMQ_SERVER = "amqp://dtnemu:dtnemu.16@10.161.3.181/?heartbeat_interval=3600"
    OPTIONS = None
    MAX_CALL_BY_MINUTE = 60
    TIMEOUT = None
    NB_MAX_RETRIES = 2

    def __init__(self, config):
        super().__init__(self.MAX_CALL_BY_MINUTE, self.TIMEOUT, self.NB_MAX_RETRIES)
        self.OPTIONS = config['endpoint_options']

    def query_endpoint(self):

        if self.is_a_call_possible():
            if self.first_call_timestamp_window is None:
                self.first_call_timestamp_window = TimeUtils.current_milli_time()
            self.counter_calls += 1

            rabbit_connection = pika.BlockingConnection(pika.URLParameters(self.URL_BASE_RABBITMQ_SERVER))
            channel = rabbit_connection.channel()
            method_frame, header_frame, body = channel.basic_get(queue=self.OPTIONS)

            if method_frame is None:
                rabbit_connection.close()
                return None
            elif method_frame.NAME == 'Basic.GetEmpty':
                rabbit_connection.close()
                return None
            else:
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                rabbit_connection.close()
                recordObject = json.loads(body)
                return recordObject['payload']
        else:
            return None

    def extract_date_from_json(self, json):
        return int(json['date'])

    def extract_value_from_json(self, json):
        return float(json['value'])

    def extract_producer_from_json(self, json, adapter_file):
        return json['producer']
