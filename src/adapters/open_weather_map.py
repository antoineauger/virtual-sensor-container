from adapters.abstract_adapter import AbstractAdapter


class OpenWeatherMap(AbstractAdapter):
    def aMethod(self):
        pass

    def __init__(self, arg):
        print('INIT OK for OpenWeatherMap ' + arg)
