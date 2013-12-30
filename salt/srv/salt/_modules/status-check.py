import json

def foo():
	with open('/proc/diskstats', 'r') as file:
		return json.dumps(file.readlines())

