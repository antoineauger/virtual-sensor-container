import json

import pika

from adapters.abstract_adapter import AbstractAdapter
from utils.json_post_observations import post_obs_to_kafka_topic

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
    kafka_producer = None
    publish_to = None

    def on_message(self, channel, method_frame, header_frame, body):
        json_obj = json.loads(body)['payload']
        if json_obj is not None:
            dict_to_send = dict(
                {
                    'date': '{}'.format(self.extract_date_from_json(json_obj)),
                    'value': str('{0:.{1}f}'.format(self.extract_value_from_json(json_obj), 3)),
                    'producer': self.extract_producer_from_json(json_obj, 'hint_rabbitmq'),
                    'timestamps': 'produced:{}'.format(self.extract_date_from_json(json_obj))
                }
            )
            post_obs_to_kafka_topic(kafka_producer=self.kafka_producer,
                                    topic=self.publish_to,
                                    dictionary=dict_to_send)
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def __init__(self, config):
        super().__init__(self.MAX_CALL_BY_MINUTE, self.TIMEOUT, self.NB_MAX_RETRIES)
        self.OPTIONS = config['endpoint_options']
        self.parameters = pika.URLParameters(self.URL_BASE_RABBITMQ_SERVER)
        self.rabbit_connection = pika.BlockingConnection(self.parameters)
        self.channel = self.rabbit_connection.channel()

    def __del__(self):
        self.rabbit_connection.close()

    def set_special_async_callback(self, kafka_producer, publish_to):
        self.kafka_producer = kafka_producer
        self.publish_to = publish_to

    def pull_endpoint(self):
        self.channel.basic_consume(self.on_message, self.OPTIONS)
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()

    def extract_date_from_json(self, json):
        return int(json['date'])

    def extract_value_from_json(self, json):
        return float(json['value'])

    def extract_producer_from_json(self, json, adapter_file):
        return json['producer']
