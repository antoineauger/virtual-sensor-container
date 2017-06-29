import requests

from adapters.abstract_adapter import AbstractAdapter
from utils.time_utils import TimeUtils


class OpenWeatherMapTemp(AbstractAdapter):
    """
    A custom adapter for the API of the OpenWeatherMap website
    Options of the form: ?q=London&appid=API_KEY
    See http://openweathermap.org/api
    """

    URL_BASE_TO_RETRIEVE = "http://api.openweathermap.org/data/2.5/weather"
    OPTIONS = ""
    MAX_CALL_BY_MINUTE = 60
    TIMEOUT = 1.0  # (in seconds)
    NB_MAX_RETRIES = 2

    def __init__(self, config):
        super().__init__(self.MAX_CALL_BY_MINUTE, self.TIMEOUT, self.NB_MAX_RETRIES)
        self.OPTIONS = config['endpoint_options']

    def query_endpoint(self):
        success = False
        temp_counter = 0

        while not success and temp_counter < self.NB_MAX_RETRIES:
            if self.is_a_call_possible():
                if self.first_call_timestamp_window is None:
                    self.first_call_timestamp_window = TimeUtils.current_milli_time()
                self.counter_calls += 1
                temp_counter += 1

                response = requests.get(self.URL_BASE_TO_RETRIEVE + self.OPTIONS,
                                        timeout=self.TIMEOUT)

                if response.status_code == requests.codes.ok and response.json() is not None:
                    try:
                        return response.json()
                    except ValueError:
                        return None
            else:
                return None

    def extract_date_from_json(self, json):
        return int(json['dt'])

    def extract_value_from_json(self, json):
        return float(json['main']['temp'])

    def extract_producer_from_json(self, json, adapter_file):
        return adapter_file
