class AngularCSRFRename(object):
    ANGULAR_HEADER_NAME = 'HTTP_X_XSRF_TOKEN'
    def process_request(self, request):
        if self.ANGULAR_HEADER_NAME in request.META:
            request.META['HTTP_X_CSRFTOKEN'] = request.META[self.ANGULAR_HEADER_NAME]
            del request.META[self.ANGULAR_HEADER_NAME]
        return None
