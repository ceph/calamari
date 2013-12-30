import json

with open('/proc/diskstats', 'r') as file:
	print(json.dumps(file.readlines()))
	