import importlib
import random

from utils.time_utils import TimeUtils


class ObsGenerator(object):
    """
    Observation generator class
    2 modes:
    -read observations from file [OK]
    -generate them according to the etc/sensor.config file [TODO]
    """
    def __init__(self, config, capabilities):
        self.config = config
        self.obs_generation_mode = self.config['obs_generation_mode']  # provided from file or generated
        self.path_obs_file = self.config['path_obs_file']  # location of the raw data file
        self.timestamp_in_milliseconds = self.config['timestamp_in_milliseconds']
        self.trust = float(self.config['trust'])/100

        self.adapterInstance = None

        self.min_bound = None
        self.max_bound = None
        self.finalMin = None
        self.finalMax = None

        if self.obs_generation_mode == "FILE" or self.obs_generation_mode == "FILE_WITH_CURRENT_DATE":
            self.raw_obs_file = open(self.path_obs_file, 'r')
        elif self.obs_generation_mode == "RANDOM":
            self.min_bound = float(capabilities['min_value'])
            self.max_bound = float(capabilities['max_value'])
        elif self.obs_generation_mode == "ADAPTER":
            my_module = importlib.import_module("adapters." + self.config['adapter_file'])
            adapter_class = getattr(my_module, self.config['adapter_class'])
            self.adapterInstance = adapter_class('Coucou')
        else:
            self.obs_generation_mode = self.obs_generation_mode.replace("\"", "")
            self.obs_generation_mode = self.obs_generation_mode.replace("[", "")
            self.obs_generation_mode = self.obs_generation_mode.replace("]", "")
            self.min_bound = float(self.obs_generation_mode.split(",")[0])
            self.max_bound = float(self.obs_generation_mode.split(",")[1])

        # If the observations are generated, we have to consider the trust level
        if self.obs_generation_mode != "FILE" and self.obs_generation_mode != "FILE_WITH_CURRENT_DATE":
            self.finalMin = self.min_bound - ((self.max_bound - self.min_bound) / 2) * (1.0 - self.trust)
            self.finalMax = self.max_bound + ((self.max_bound - self.min_bound) / 2) * (1.0 - self.trust)

    def generate_one_observation(self, sensor_id):
        """
        Read a line (i.e., observation) of the specified file.
        At the end of the file, the method close the file descriptor.
        :returns a single observation (i.e., a single line of the provided raw data file)
        :rtype str or None (if no more observations)
        """
        dict_to_send = None

        if self.obs_generation_mode == "FILE" or self.obs_generation_mode == "FILE_WITH_CURRENT_DATE":
            line = self.raw_obs_file.readline()
            if line == '':
                self.raw_obs_file.close()
                line = None

            if line is not None:
                formatted_obs = line.strip('\n').split(' ')

                if self.timestamp_in_milliseconds == "false":
                    formatted_obs[0] = int(float(formatted_obs[0])) * 1000
                formatted_obs[1] = float(formatted_obs[1])

                dict_to_send = dict(
                    {
                        'date': str(formatted_obs[0]),
                        'value': str('{0:.{1}f}'.format(formatted_obs[1], 3)),
                        'producer': sensor_id,
                        'timestamps': 'produced:' + str(TimeUtils.current_milli_time())
                    }
                )
        elif self.obs_generation_mode == "ADAPTER":
            pass
        else:
            date_now = TimeUtils.current_milli_time()
            dict_to_send = dict(
                {
                    'date': '{}'.format(date_now),
                    'value': str('{0:.{1}f}'.format(random.uniform(self.finalMin, self.finalMax), 3)),
                    'producer': sensor_id,
                    'timestamps': 'produced:{}'.format(date_now)
                }
            )

        return dict_to_send
