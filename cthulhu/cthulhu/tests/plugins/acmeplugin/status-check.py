import json

class StatusCheck(object):

	@property
	def frequency(self):
		"""
		How often in milliseconds the monitor will invoke this status check
		"""
		return 5000

	def run(self):
		with open('/proc/diskstats', 'r') as file:
			print(json.dumps(file.readlines()))
	