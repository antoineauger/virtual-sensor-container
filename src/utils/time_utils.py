import time


class TimeUtils(object):
    @staticmethod
    def current_milli_time():
        return int(round(time.time() * 1000))
