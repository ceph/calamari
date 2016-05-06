from django.conf import settings
from django.http import HttpResponseRedirect


class AngularCSRFRename(object):
    ANGULAR_HEADER_NAME = 'HTTP_X_XSRF_TOKEN'

    def process_request(self, request):
        if self.ANGULAR_HEADER_NAME in request.META:
            request.META['HTTP_X_CSRFTOKEN'] = request.META[self.ANGULAR_HEADER_NAME]
            del request.META[self.ANGULAR_HEADER_NAME]
        return None


class SSLRedirect:
    
    def process_request(self, request):
        if request.META['wsgi.url_scheme'] != 'https':
            return self._redirect(request, True)

    def _is_secure(self, request):
        if request.is_secure():
            return True

        # Handle the Webfaction case until this gets resolved in the request.is_secure()
        if 'HTTP_X_FORWARDED_SSL' in request.META:
            return request.META['HTTP_X_FORWARDED_SSL'] == 'on'

        return False

    def _redirect(self, request, secure):
        protocol = secure and "https" or "http"
        http_host = request.META["HTTP_HOST"]
        http_host.replace(":8002", ":8003")
        host = getattr(settings, 'SSL_HOST', http_host)
        newurl = "%s://%s%s" % (protocol, host, request.get_full_path())
        if settings.DEBUG and request.method == 'POST':
            raise RuntimeError, \
                """Django can't perform a SSL redirect while maintaining POST data.
                Please structure your views so that redirects only occur during GETs."""

        return HttpResponseRedirect(newurl)
