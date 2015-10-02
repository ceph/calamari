

"""
Helpers for writing django views and rest_framework ViewSets that get
their data from cthulhu with zeroRPC
"""
from collections import defaultdict
import logging

# Suppress warning from ZeroRPC's use of old gevent API
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning,
                        message=".*Queue\(0\) now equivalent to Queue\(None\);.*")
warnings.filterwarnings("ignore", category=DeprecationWarning,
                        message=".*gevent.coros has been renamed to gevent.lock.*")

from rest_framework import status
import time

from rest_framework.response import Response

try:
    from zerorpc import LostRemote, RemoteError
    import zerorpc
except ImportError:
    zerorpc = None

from calamari_common.config import CalamariConfig
from calamari_common.types import NotFound
from calamari_rest.viewsets import RoleLimitedViewSet
from rest_framework.viewsets import ViewSet
config = CalamariConfig()


class DataObject(object):
    """
    A convenience for converting dicts from the backend into
    objects, because django_rest_framework expects objects
    """
    def __init__(self, data):
        self.__dict__.update(data)


if zerorpc is not None:
    class ProfiledRpcClient(zerorpc.Client):
        # Finger in the air, over 100ms is too long
        SLOW_THRESHOLD = 0.2

        def __init__(self, *args, **kwargs):
            super(ProfiledRpcClient, self).__init__(*args, **kwargs)

            self.method_times = defaultdict(list)

        def _process_response(self, request_event, bufchan, timeout):
            a = time.time()
            result = super(ProfiledRpcClient, self)._process_response(request_event, bufchan, timeout)
            b = time.time()
            self.method_times[request_event.name].append(b - a)
            return result

        def report(self, log):
            total = 0.0
            for method_name, times in self.method_times.items():
                for t in times:
                    if t > self.SLOW_THRESHOLD:
                        log.warn("Slow RPC '%s' (%sms)" % (method_name, t * 1000))
                    total += t
                log.debug("RPC timing for '%s': %s/%s/%s avg/min/max ms" % (
                    method_name, sum(times) * 1000.0 / len(times), min(times) * 1000.0, max(times) * 1000.0
                ))
            log.debug("Total time in RPC: %sms" % (total * 1000))
else:
    class ProfiledRpcClient(object):
        pass


class RPCViewSet(ViewSet):
    serializer_class = None
    log = logging.getLogger('django.request.profile')

    def __init__(self, *args, **kwargs):
        if zerorpc is None:
            raise RuntimeError("Cannot run without zerorpc")

        super(RPCViewSet, self).__init__(*args, **kwargs)
        self.client = ProfiledRpcClient()

    def dispatch(self, request, *args, **kwargs):
        self.client.connect(config.get('cthulhu', 'rpc_url'))
        a = time.time()
        try:
            return super(RPCViewSet, self).dispatch(request, *args, **kwargs)
        finally:
            b = time.time()
            self.client.close()
            self.log.debug("[%sms] %s" % ((b - a) * 1000.0, request.path))
            self.client.report(self.log)

    @property
    def help(self):
        return self.__doc__

    @property
    def help_summary(self):
        return ""

    def handle_exception(self, exc):
        try:
            return super(RPCViewSet, self).handle_exception(exc)
        except LostRemote as e:
            return Response({'detail': "RPC error ('%s')" % e},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE, exception=True)
        except RemoteError as e:
            if e.name == 'NotFound':
                return Response(str(e.msg), status=status.HTTP_404_NOT_FOUND)
            elif e.name == 'BucketNotEmptyError':
                return Response(str(e.msg), status=status.HTTP_409_CONFLICT)
            else:
                raise
        except NotFound as e:
                return Response(str(e), status=status.HTTP_404_NOT_FOUND)

    def metadata(self, request):
        ret = super(RPCViewSet, self).metadata(request)

        actions = {}
        # TODO: get the fields marked up with whether they are:
        # - [allowed|required|forbidden] during [creation|update] (6 possible kinds of field)
        # e.g. on a pool
        # id is forbidden during creation and update
        # pg_num is required during create and optional during update
        # pgp_num is optional during create or update
        # nothing is required during update
        if hasattr(self, 'update'):
            if self.serializer_class:
                actions['PATCH'] = self.serializer_class().metadata()
        if hasattr(self, 'create'):
            if self.serializer_class:
                actions['POST'] = self.serializer_class().metadata()
        ret['actions'] = actions

        return ret
