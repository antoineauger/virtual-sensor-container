from utils.time_utils import TimeUtils


class AbstractAdapter(object):
    """AbstractAdapter to build adapters in order to retrieve observation from a WebService or a website API."""

    def __init__(self, max_call_by_minute, timeout, nb_max_retries):
        self.first_call_timestamp_window = None
        self.counter_calls = 0
        self.max_call_by_minute = max_call_by_minute
        self.timeout = timeout
        self.nb_max_retries = nb_max_retries

    def is_a_call_possible(self):
        if self.counter_calls + 1 < self.max_call_by_minute:
            return True
        elif TimeUtils.current_milli_time() - self.first_call_timestamp_window > 60000:
            self.first_call_timestamp_window = None
            self.counter_calls = 0
            return True
        else:
            return False

    # The following methods should be implemented when creating a new adapter from scratch.

    def query_endpoint(self):
        raise NotImplementedError("Should have implemented this")

    def extract_date_from_json(self, json):
        raise NotImplementedError("Should have implemented this")

    def extract_value_from_json(self, json):
        raise NotImplementedError("Should have implemented this")
