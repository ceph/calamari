import json

class StatusProcessor(object):
    # this defines how often status_checks are run
    period = 1

    def run(status_check_data):
        """
        status_check_data is expected to be a dict that is (minion_id to whatever is output by the status_check)
        return of this function is JSON
        """
        return json.dumps({status_check_data})        
