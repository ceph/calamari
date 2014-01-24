class StatusProcessor(object):

    @property
    def period(self):
        """
        How often the Plugin runs in seconds
        """
        return 1

    def run(self, check_data):
        """
        status_check_data is expected to be a dict that is (minion_id to whatever is output by the status_check)
        return of this function is JSON
        """

        state = "OK"
        for node, data in check_data.iteritems():
            for key, value in data.iteritems():
                if key == 'SMART Health Status' and value != "OK":
                    state = "FAIL"

        return {'SMART Health Status': state}
