import time


class ObsGenerator(object):
	"""
	    Observation generator class
	    2 modes:
	        -read observations from file [OK]
	        -generate them according to the etc/sensor.config file [TODO]
	"""

	def __init__(self, config):
		# TODO refactor to allow to swith between modes
		self.config = config
		self.generation_method_obs = self.config['generation_method_obs']  # provided from file or generated
		self.path_obs_file = self.config['path_obs_file']  # location of the raw data file
		self.timestamp_in_milliseconds = self.config['timestamp_in_milliseconds']
		self.raw_obs_file = open(self.path_obs_file, 'r')

	@staticmethod
	def current_milli_time():
		return int(round(time.time() * 1000))

	def generate_one_observation(self, sensor_id):
		"""
			Read a line (i.e., observation) of the specified file.
			At the end of the file, the method close the file descriptor.
			:returns a single observation (i.e., a single line of the provided raw data file)
			:rtype str or None (if no more observations)
		"""
		dict_to_send = None
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
					'value': str(formatted_obs[1]),
					'producer': sensor_id,
					'timestamps': 'produced:' + str(self.current_milli_time())
				 }
			)

		return dict_to_send
