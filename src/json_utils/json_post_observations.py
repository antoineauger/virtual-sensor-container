import requests


def post_obs_to_rest_endpoint(url, dictionary):
    """
        Method to POST a dict object (transformed in a JSON payload) to a REST endpoint
        :param url: str
        :param dictionary: the dictionnary to send (dict)
    """
    requests.post(url=url,
                  json=dictionary)


def post_obs_to_kafka_topic(kafka_producer, topic, dictionary):
    kafka_producer.send(topic, dictionary)
    kafka_producer.flush()
